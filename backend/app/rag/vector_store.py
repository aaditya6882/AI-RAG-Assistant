import psycopg  # pyright: ignore[reportMissingImports]

from pgvector.psycopg import register_vector  # pyright: ignore[reportMissingImports]

from app.config import PSYCOPG_DATABASE_URL


def get_connection():
    connection = psycopg.connect(PSYCOPG_DATABASE_URL, connect_timeout=5)

    register_vector(connection)

    return connection


def init_schema():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    page_number INTEGER,
                    chunk_index INTEGER,
                    embedding vector(768)
                )
                """
            )
        connection.commit()


def list_documents():
    init_schema()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    document_name,
                    COUNT(*) AS chunks,
                    MAX(page_number) AS pages
                FROM document_chunks
                GROUP BY document_name
                ORDER BY document_name
                """
            )
            return [
                {
                    "document": row[0],
                    "chunks": row[1],
                    "pages": row[2],
                }
                for row in cursor.fetchall()
            ]


def save_chunks(
    document_name: str,
    documents,
    embeddings: list[list[float]],
):
    if len(documents) != len(embeddings):
        raise ValueError(
            "Number of documents and embeddings must be the same."
        )

    init_schema()

    with get_connection() as connection:
        with connection.cursor() as cursor:

            for index, (document, embedding) in enumerate(
                zip(documents, embeddings)
            ):
                page_number = document.metadata.get("page")

                if page_number is not None:
                    page_number = int(page_number) + 1

                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        document_name,
                        content,
                        page_number,
                        chunk_index,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        document_name,
                        document.page_content,
                        page_number,
                        index,
                        embedding,
                    ),
                )

        connection.commit()


def search_similar_chunks(
    query_embedding: list[float],
    limit: int = 5,
    max_distance: float = 0.5,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    document_name,
                    content,
                    page_number,
                    chunk_index,
                    embedding <=> %s::vector AS distance
                FROM document_chunks
                WHERE embedding <=> %s::vector <= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding,
                    query_embedding,
                    max_distance,
                    query_embedding,
                    limit,
                ),
            )

            return cursor.fetchall()