from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from app.rag.embeddings import get_query_embeddings
from app.rag.vector_store import search_similar_chunks


class PGVectorRetriever(BaseRetriever):

    embedding_model: object = Field(exclude=True)
    limit: int = 5
    max_distance: float = 0.5

    def _get_relevant_documents(self, query: str) -> list[Document]:

        # Convert question into embedding
        query_embedding = self.embedding_model.embed_query(query)

        # Search PostgreSQL
        results = search_similar_chunks(
            query_embedding,
            limit=self.limit,
            max_distance=self.max_distance,
        )

        # Convert database rows into LangChain Documents
        documents = []

        for row in results:
            document = Document(
                page_content=row[1],
                metadata={
                    "document": row[0],
                    "page": row[2],
                    "chunk": row[3],
                    "distance": row[4],
                },
            )

            documents.append(document)

        return documents