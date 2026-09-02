from langchain_google_genai import ChatGoogleGenerativeAI  # pyright: ignore[reportMissingImports]

from app.config import GOOGLE_API_KEY
from app.rag.embeddings import get_query_embeddings
from app.rag.vector_store import search_similar_chunks


def answer_question(question: str, limit: int = 5):

    # 1. Create query embedding model
    embedding_model = get_query_embeddings()

    # 2. Convert user's question into an embedding
    query_embedding = embedding_model.embed_query(question)

    # 3. Search PostgreSQL for similar chunks
    results = search_similar_chunks(
        query_embedding,
        limit=limit,
    )

    # 4. Build context from retrieved chunks
    context = "\n\n".join(
        f"[Page {row[2]}]\n{row[1]}"
        for row in results
    )

    # 5. Create Gemini chat model
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    # 6. Create RAG prompt
    prompt = f"""
You are a helpful assistant answering questions
using the provided document context.

Use ONLY the information provided in the context.

If the answer is not contained in the context,
say that you don't know based on the uploaded documents.

Do not invent information.

Context:
{context}

Question:
{question}

Answer:
"""

    # 7. Send prompt to Gemini
    response = llm.invoke(prompt)

    # 8. Return answer and sources
    return {
        "answer": response.content,
        "sources": [
            {
                "document_name": row[0],
                "page_number": row[2],
                "chunk_index": row[3],
                "distance": row[4],
            }
            for row in results
        ],
    }