import psycopg

from pgvector.psycopg import register_vector

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