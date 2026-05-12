import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langdetect import detect
from openai import OpenAI

from rag import RAGStore
from booking_tools import check_availability, quote_price, create_booking_link
from prompts import SYSTEM_PROMPT

# In Colab, we'll read OPENAI_API_KEY from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found. Set it in Colab: os.environ['OPENAI_API_KEY']='...'")

client = OpenAI(api_key=api_key)

app = FastAPI(title="Cabin Chatbot Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
rag = RAGStore(openai_api_key=api_key)
rag.ingest_if_empty()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    checkin: str | None = None
    checkout: str | None = None
    guests: int | None = None
    pets: bool | None = None
    cabin_type: str | None = None

def detect_lang(text: str) -> str:
    try:
        l = detect(text)
        return "es" if l.startswith("es") else "en"
    except:
        return "en"

def needs_availability(msg: str) -> bool:
    m = msg.lower()
    return any(x in m for x in [
        "availability","available","vacant","dates","book","booking","reserve",
        "disponibilidad","disponible","reservar","reserva","fechas"
    ])

def needs_pricing(msg: str) -> bool:
    m = msg.lower()
    return any(x in m for x in [
        "price","rate","cost","how much","pricing",
        "precio","tarifa","costo","cuánto","cuanto"
    ])

@app.post("/chat")
def chat(req: ChatRequest):
    user_lang = detect_lang(req.message)
    do_avail = needs_availability(req.message)
    do_price = needs_pricing(req.message)

    tool_context = ""

    # Availability + pricing uses structured tools
    if do_avail:
        if not (req.checkin and req.checkout and req.guests):
            return {"reply": "Claro. ¿Qué fechas (check-in y check-out) y cuántos huéspedes serán?"
                    if user_lang == "es"
                    else "Sure — what check-in/check-out dates and how many guests?"}

        available = check_availability(
            checkin=req.checkin,
            checkout=req.checkout,
            guests=req.guests,
            cabin_type=req.cabin_type,
            pets=bool(req.pets)
        )
        tool_context += f"\nAVAILABILITY_RESULT: {available}\n"

        if do_price and available:
            cabin_type = available[0]["type"]
            price = quote_price(
                req.checkin, req.checkout, cabin_type,
                pets=bool(req.pets),
                num_pets=1 if req.pets else 0
            )
            tool_context += f"\nPRICE_QUOTE: {price}\n"

        if available:
            link = create_booking_link(req.checkin, req.checkout, available[0]["cabin_id"], req.guests)
            tool_context += f"\nBOOKING_LINK: {link}\n"

    # FAQ uses RAG
    if not do_avail:
        snippets = rag.search(req.message, lang=user_lang, k=4)
        tool_context += "\nKNOWLEDGE_SNIPPETS:\n"
        for s in snippets:
            tool_context += f"- ({s['meta']['source']}) {s['text']}\n"

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User language: {user_lang}\nUser message: {req.message}\n\nContext:\n{tool_context}"}
        ],
        temperature=0.4
    )

    return {"reply": completion.choices[0].message.content}
