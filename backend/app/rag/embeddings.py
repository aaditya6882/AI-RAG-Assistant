from langchain_google_genai import GoogleGenerativeAIEmbeddings  # pyright: ignore[reportMissingImports]

from app.config import GOOGLE_API_KEY


def get_document_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
        output_dimensionality=768,
        task_type="RETRIEVAL_DOCUMENT",
    )


def get_query_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
        output_dimensionality=768,
        task_type="RETRIEVAL_QUERY",
    )