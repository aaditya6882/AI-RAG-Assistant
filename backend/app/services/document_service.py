from pathlib import Path

from app.rag.embeddings import get_document_embeddings
from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vector_store import save_chunks


def process_pdf(file_path: str):
    path = Path(file_path)

    # 1. Load PDF
    documents = load_pdf(str(path))

    if not documents:
        raise ValueError("PDF contains no readable text.")

    # 2. Split into chunks
    chunks = split_documents(documents)

    if not chunks:
        raise ValueError("No chunks were generated from the PDF.")

    # 3. Generate embeddings
    embedding_model = get_document_embeddings()

    embeddings = embedding_model.embed_documents(
        [chunk.page_content for chunk in chunks]
    )

    # 4. Save into PostgreSQL + pgvector
    save_chunks(
        document_name=path.name,
        documents=chunks,
        embeddings=embeddings,
    )

    return {
        "document": path.name,
        "pages": len(documents),
        "chunks": len(chunks),
    }