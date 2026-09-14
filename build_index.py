"""
Builds the Chroma vector index from data/raw/*.txt (produced by scraper.py).

Run:
    python build_index.py
"""

import json
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "data/raw"
CHROMA_DIR = "chroma_db"
MANIFEST_PATH = os.path.join(DATA_DIR, "manifest.json")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_manifest_lookup():
    """filename -> {url, doc_type, fetched_at, title}"""
    if not os.path.exists(MANIFEST_PATH):
        print(f"WARNING: no manifest found at {MANIFEST_PATH}. Run scraper.py first.")
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return {entry["filename"]: entry for entry in entries}


def main():
    print("Loading documents from", DATA_DIR)
    loader = DirectoryLoader(
        DATA_DIR, glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")

    lookup = load_manifest_lookup()

    for doc in documents:
        filename = os.path.basename(doc.metadata.get("source", ""))
        entry = lookup.get(filename, {})
        doc.metadata["filename"] = filename
        doc.metadata["source_url"] = entry.get("url", "Unknown source")
        doc.metadata["doc_type"] = entry.get("doc_type", "unknown")
        doc.metadata["fetched_at"] = entry.get("fetched_at", "unknown")

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model (first run downloads it, can take a minute)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print("Embedding and storing in ChromaDB...")
    Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=CHROMA_DIR)

    print(f"\nDone. Stored {len(chunks)} chunks in '{CHROMA_DIR}'. Index ready.")


if __name__ == "__main__":
    main()