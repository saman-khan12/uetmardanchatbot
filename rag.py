"""
Core RAG logic for the UET Mardan assistant.

No keyword-routing tables. Every question goes through the same path:
  1. semantic similarity search against the Chroma index
  2. build a prompt containing (a) the small set of verified facts from
     facts.py and (b) the retrieved chunks
  3. ask the LLM to answer using only that context, in its own words

Both server.py (the web UI) and cli.py (terminal chat) import
`answer_question` from here, so there is exactly one place the answering
logic lives.
"""

import os

from dotenv import load_dotenv
from ollama import Client
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

from facts import VERIFIED_FACTS

load_dotenv()

CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
MAX_CONTEXT_CHARS = 12000
MAX_OUTPUT_TOKENS = 500
RETRIEVAL_K = 6

if not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY not found. Add it to your .env file: OLLAMA_API_KEY=your_key")

PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
You are a helpful assistant that answers questions about UET Mardan
(University of Engineering & Technology, Mardan).

Answer using ONLY the information below. If the verified facts and the
retrieved context ever disagree, trust the verified facts.

Rules:
- Default to SHORT answers: 2-4 sentences, or a tight bullet list of at most
  4-5 items. Only go longer than that if the question truly requires a
  multi-step walkthrough (e.g. "walk me through the whole admission
  process").
- Do not add a title/header line, do not add sub-bullets under bullets, and
  do not use emoji, unless the question specifically asks for a detailed
  step-by-step guide.
- Answer clearly and directly when the information is present. Do not pad
  the answer with restated context, disclaimers, or closing summaries.
- Always express information in your own words. Do not copy or closely
  paraphrase sentences verbatim — restate facts naturally.
- Whenever the answer involves an action the user would take next (applying,
  filling a form, checking a schedule, viewing fees, downloading a
  prospectus or a form, etc.) and a relevant link exists in the "IMPORTANT
  LINKS" or "DOWNLOADABLE FORMS" section of the verified facts, include it
  as a Markdown link with clear, descriptive text, e.g.
  [UET Mardan online admissions portal](https://...). Place it naturally at
  the end of the relevant point, not just at the end of the whole answer.
- Do not invent or guess a URL. Only use a link if it appears in the
  verified facts or retrieved context.
- If neither the verified facts nor the retrieved context answers the
  question, say you don't have that information and suggest checking
  uetmardan.edu.pk directly. Do not guess or invent facts.

Verified facts:
{facts}

Retrieved context:
{context}

Question: {question}

Answer:
""")

print("Loading embedding model...")
_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

print("Loading Chroma index...")
_vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=_embeddings)

_ollama_client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
)


def _call_ollama(prompt, retry=True):
    try:
        response = _ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.2 if retry else 0.4,
                "num_predict": MAX_OUTPUT_TOKENS,
            },
        )
        result = (response.get("message", {}).get("content") or "").strip()
    except Exception as error:  # noqa: BLE001 - surfaced to caller in answer_question
        print(f"[DEBUG] Ollama call failed: {error}")
        raise

    print(f"[DEBUG] result_len={len(result)}")

    if not result and retry:
        nudge = prompt + (
            "\n\nIMPORTANT: Answer in 3-5 short sentences or a brief bullet list. "
            "Do not over-explain."
        )
        return _call_ollama(nudge, retry=False)

    return result


def answer_question(question, k=RETRIEVAL_K):
    """Retrieve relevant chunks and generate an answer. Returns (answer, sources)."""
    results = _vectordb.similarity_search(question, k=k)

    context_text = "\n\n---\n\n".join(doc.page_content for doc in results)[:MAX_CONTEXT_CHARS]
    sources = sorted({doc.metadata.get("source_url", "Unknown") for doc in results})

    prompt = PROMPT_TEMPLATE.format(facts=VERIFIED_FACTS, context=context_text, question=question)

    try:
        answer = _call_ollama(prompt)
    except Exception as error:  # noqa: BLE001
        error_text = str(error).lower()
        if "429" in error_text or "rate" in error_text or "quota" in error_text:
            answer = (
                "The assistant is temporarily unavailable because usage limits were "
                "reached. Here's what the verified facts say:\n\n" + VERIFIED_FACTS[:2000]
                + "\n\nPlease try again later or check uetmardan.edu.pk."
            )
        else:
            answer = (
                "The assistant is temporarily unavailable right now. Please try again shortly, "
                "or check uetmardan.edu.pk directly."
            )

    if not answer:
        answer = "I couldn't generate an answer."

    return answer, sources