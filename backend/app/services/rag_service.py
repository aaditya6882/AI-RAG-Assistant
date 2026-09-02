from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import GOOGLE_API_KEY
from app.rag.embeddings import get_query_embeddings
from app.rag.retriever import PGVectorRetriever


def format_documents(documents):
    return "\n\n".join(
        f"[Page {document.metadata.get('page')}]\n"
        f"{document.page_content}"
        for document in documents
    )


def answer_question(question: str, limit: int = 5):

    # Create retriever
    retriever = PGVectorRetriever(
        embedding_model=get_query_embeddings(),
        limit=limit,
        max_distance=0.5,
    )

    # Create Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    # Prompt
    prompt = ChatPromptTemplate.from_template(
        """
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
    )

    # Retrieve documents and create context
    retrieval_chain = (
    RunnablePassthrough.assign(
        documents=lambda x: retriever.invoke(x["question"])
    )
    .assign(
        context=lambda x: format_documents(x["documents"])
    )
)

    # Run retrieval
    result = retrieval_chain.invoke({
    "question": question
})

    # Check if documents were found
    if not result["documents"]:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents.",
            "sources": [],
        }

    # Generate answer
    generation_chain = prompt | llm | StrOutputParser()

    answer = generation_chain.invoke(
        {
            "context": result["context"],
            "question": question,
        }
    )

    # Sources come from the SAME retrieved documents
    sources = [
        {
            "document": document.metadata.get("document"),
            "page": document.metadata.get("page"),
            "chunk": document.metadata.get("chunk"),
        }
        for document in result["documents"]
    ]

    return {
        "answer": answer,
        "sources": sources,
    }