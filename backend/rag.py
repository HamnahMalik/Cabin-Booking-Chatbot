import os, glob, re
import chromadb
from chromadb.utils import embedding_functions

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "kb_docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chroma")

def _load_md_files():
    paths = glob.glob(os.path.join(KB_DIR, "*.md"))
    docs = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            text = f.read().strip()
        fname = os.path.basename(p)
        lang = "es" if fname.startswith("es_") else "en"
        docs.append((fname, lang, text))
    return docs

def _chunk_md(text: str):
    parts = re.split(r"\n(?=# )|\n(?=## )|\n(?=### )", text)
    chunks = []
    for c in parts:
        c = c.strip()
        if len(c) >= 60:
            chunks.append(c)
    return chunks

class RAGStore:
    def __init__(self, openai_api_key: str):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embedder = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
        self.col = self.client.get_or_create_collection(
            name="kb_docs",
            embedding_function=self.embedder
        )

    def ingest_if_empty(self):
        if self.col.count() > 0:
            return

        docs = _load_md_files()
        ids, texts, metas = [], [], []
        idx = 0
        for fname, lang, content in docs:
            for chunk in _chunk_md(content):
                ids.append(f"{fname}-{idx}")
                texts.append(chunk)
                metas.append({"source": fname, "lang": lang})
                idx += 1

        if ids:
            self.col.add(ids=ids, documents=texts, metadatas=metas)

    def search(self, query: str, lang: str = "en", k: int = 4):
        # Prefer same-language results
        res = self.col.query(query_texts=[query], n_results=k, where={"lang": lang})
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]

        # Fallback: any language
        if not docs:
            res = self.col.query(query_texts=[query], n_results=k)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]

        return [{"text": d, "meta": m} for d, m in zip(docs, metas)]
