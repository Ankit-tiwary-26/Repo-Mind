import chromadb
from app.config import settings

_client = chromadb.PersistentClient(path=settings.chroma_path)


def get_collection(project_id: str):
    return _client.get_or_create_collection(name=f"project_{project_id}")


def add_chunks(project_id: str, chunks: list[dict]):
    if not chunks:
        return
    collection = get_collection(project_id)
    ids = [f"{c['metadata']['path']}:{c['metadata']['start_line']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    # Chroma batches internally; for very large repos, chunk this into batches of ~500
    batch = 500
    for i in range(0, len(ids), batch):
        collection.upsert(
            ids=ids[i:i + batch],
            documents=documents[i:i + batch],
            metadatas=metadatas[i:i + batch],
        )


def query(project_id: str, question: str, n_results: int = 8) -> list[dict]:
    collection = get_collection(project_id)
    results = collection.query(query_texts=[question], n_results=n_results)
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits

def delete_collection(project_id: str):
    try:
        _client.delete_collection(name=f"project_{project_id}")
    except Exception:
        pass
