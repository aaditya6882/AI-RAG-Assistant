from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader  # pyright: ignore[reportMissingImports]


def load_pdf(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are currently supported.")

    loader = PyPDFLoader(str(path))

    return loader.load()