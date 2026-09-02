import psycopg  # pyright: ignore[reportMissingImports]

from pgvector.psycopg import register_vector  # pyright: ignore[reportMissingImports]

from app.config import DATABASE_URL


def get_connection():
    connection = psycopg.connect(DATABASE_URL)

    register_vector(connection)

    return connection


def save_chunks(
    document_name: str,
    documents,
    embeddings: list[list[float]],
):
    if len(documents) != len(embeddings):
        raise ValueError(
            "Number of documents and embeddings must be the same."
        )

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