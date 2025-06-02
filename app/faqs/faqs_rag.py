import os
import json
import time
from sentence_transformers import SentenceTransformer
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

FAQ_JSON_PATH = "app/faqs/data"
MODEL_LOCAL_PATH = "./models/bge-base-en-v1.5"
FAISS_INDEX_PATH = "./faiss_index"
DEVICE = "cpu"

def load_faq_files(path):
    print(f"Scanning for JSON files in '{path}'...")
    json_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    print(f"Found {len(json_files)} JSON file(s).")
    return json_files

def parse_faq_data(json_files):
    docs = []
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for item in data:
                    q = item.get("question", "").strip()
                    a = item.get("answer", "").strip()
                    if q and a:
                        docs.append(Document(
                            page_content=f"Q: {q}\nA: {a}",
                            metadata={"question": q, "answer": a}
                        ))
            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON: {json_file}")
    print(f"✅ Loaded {len(docs)} document(s).")
    return docs

def ensure_embedding_model(path):
    if not os.path.exists(path):
        # print("Downloading embedding model...")
        model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        model.save(path)
        print("Model downloaded and saved.")
    else:
        print("Embedding model already exists locally.")

def create_faiss_index(docs, model_path):
    print("Loading embedding model...")
    embedding = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"device": DEVICE},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    print(" Creating FAISS vector store...")
    start = time.time()
    vectorstore = FAISS.from_documents(docs, embedding)
    print(f" FAISS index created in {time.time() - start:.2f}s.")
    return vectorstore

def save_faiss_index(vectorstore, path):
    print(f"Saving FAISS index to '{path}'...")
    vectorstore.save_local(path)
    print("Index saved successfully.")

def main():
    json_files = load_faq_files(FAQ_JSON_PATH)
    print("Parsing FAQ data...")
    docs = parse_faq_data(json_files)
    ensure_embedding_model(MODEL_LOCAL_PATH)
    vectorstore = create_faiss_index(docs, MODEL_LOCAL_PATH)
    save_faiss_index(vectorstore, FAISS_INDEX_PATH)
    print("All done!")




