import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

VECTOR_DIR = "./faiss_index"
PDF_file_path = "./樂園營運手冊.pdf"


def load_vector_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cuda"}
    )

    if os.path.exists(VECTOR_DIR):
        return FAISS.load_local(
            VECTOR_DIR, embeddings, allow_dangerous_deserialization=True
        )

    loader = PyPDFLoader(PDF_file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=150
    )

    texts = splitter.split_documents(docs)

    db = FAISS.from_documents(texts, embeddings)
    db.save_local(VECTOR_DIR)

    return db