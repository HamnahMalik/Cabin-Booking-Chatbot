# AI Cabin Booking Chatbot (RAG + FastAPI)

An AI-powered multilingual cabin booking chatbot built using FastAPI, OpenAI, ChromaDB, and Retrieval-Augmented Generation (RAG). The chatbot supports semantic FAQ retrieval, cabin availability checking, dynamic pricing estimation, and multilingual customer interaction through a custom frontend interface.

---

## Features

* Retrieval-Augmented Generation (RAG)
* Semantic FAQ retrieval using vector embeddings
* Multilingual support (English & Spanish)
* Cabin availability checking
* Dynamic pricing estimation
* Interactive frontend chat interface
* FastAPI backend
* ChromaDB vector database
* OpenAI-powered conversational responses

---

## Architecture

Frontend UI → FastAPI Backend → ChromaDB Retrieval → OpenAI LLM

---

## Tech Stack

* Python
* FastAPI
* OpenAI API
* ChromaDB
* HTML / CSS / JavaScript
* pyngrok
* NLP / RAG

---

## Knowledge Base

The chatbot uses a custom knowledge base containing:

* Cabin policies
* Amenities
* Location information
* Cabin details
* Spanish and English documentation

Documents are embedded and stored in ChromaDB for semantic retrieval.

---

## How RAG Works

1. User submits a query
2. Relevant knowledge snippets are retrieved from ChromaDB
3. Retrieved context is injected into the prompt
4. OpenAI generates a grounded response

This approach improves factual accuracy and reduces hallucinations.

---

## Example Queries

* “Do you allow dogs?”
* “What is your cancellation policy?”
* “Check availability for March 10–12”
* “¿Aceptan mascotas?”
* “How much does a deluxe cabin cost?”

---

## Project Structure

```bash
backend/
├── app.py
├── rag.py
├── booking_tools.py
├── prompts.py

frontend/
├── index.html

kb/
├── policies.md
├── amenities.md
├── cabins.md
├── location.md

data/
├── cabins.json
├── rates.json
├── availability.json
```

---

## Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set OpenAI API Key

```bash
export OPENAI_API_KEY="your_api_key"
```

### Run FastAPI server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Launch ngrok tunnel

```python
from pyngrok import ngrok
public_url = ngrok.connect(8000)
print(public_url)
```
''''''''''
### Screenshots
<img width="904" height="839" alt="Screenshot-3 Conversation" src="https://github.com/user-attachments/assets/614d3775-47aa-4df7-9b00-aa5539d41983" />
<img width="918" height="828" alt="Screenshot-2 Spanish" src="https://github.com/user-attachments/assets/3ab4e3f6-a255-40cc-a5f8-88cef2cd187c" />
<img width="902" height="786" alt="Screenshot -1" src="https://github.com/user-attachments/assets/a9a7e020-7d2e-4d2c-ae2d-01148cbf1233" />

---------
---

## Future Improvements

* Conversation memory
* Real booking database integration
* Streaming responses
* Admin dashboard
* Hybrid retrieval (BM25 + vector search)
* Authentication and user sessions

---

## License

This project is for educational and portfolio purposes.
