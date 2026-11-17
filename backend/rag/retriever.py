"""Persistent Chroma retrieval with explicit lexical-demo or semantic embeddings."""

import hashlib
import math
import re
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


def lexical_vector(text):
    """Offline feature-hashing baseline. This is NOT a learned semantic embedding."""
    vector = [0.0] * 384
    for word in re.findall(r"[\w]+", text.lower()):
        index = int(hashlib.sha256(word.encode()).hexdigest()[:8], 16) % len(vector)
        vector[index] += 1
    norm = math.sqrt(sum(v * v for v in vector)) or 1
    return [v / norm for v in vector]


class Retriever:
    def __init__(self, path, profile, mode="lexical"):
        if mode not in {"lexical", "semantic"}:
            raise ValueError("EMBEDDING_MODE must be lexical or semantic")
        self.mode, self.profile = mode, profile
        self.client = chromadb.PersistentClient(
            path=path, settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=f"{profile.business_id}-{mode}-v1",
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )
        self.semantic = DefaultEmbeddingFunction() if mode == "semantic" else None

    def embed(self, texts):
        if self.semantic:
            return [list(map(float, row)) for row in self.semantic(texts)]
        return [lexical_vector(t) for t in texts]

    def ingest(self, directory):
        """Stable chunk IDs preserve source attribution; bounded chunks limit prompt size."""
        paths = sorted(Path(directory).glob("*.md"))
        if not paths:
            raise ValueError(f"No knowledge documents found in {directory}")
        ids, docs, metadata = [], [], []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for offset in range(0, len(text), 650):
                chunk = text[offset : offset + 800]
                ids.append(f"{path.stem}:{offset}")
                docs.append(chunk)
                metadata.append(
                    {
                        "source": path.name,
                        "source_id": f"{path.stem}:{offset}",
                        "offset": offset,
                        "version": hashlib.sha256(text.encode()).hexdigest()[:12],
                    }
                )
        existing = self.collection.get()["ids"]
        if existing:
            self.collection.delete(ids=existing)
        self.collection.upsert(ids=ids, documents=docs, metadatas=metadata, embeddings=self.embed(docs))
        return len(ids)

    def search(self, query, limit=3):
        count = self.collection.count()
        if not count:
            raise ValueError("Knowledge index is empty; run scripts.seed")
        result = self.collection.query(query_embeddings=self.embed([query]), n_results=min(limit, count))
        refs = []
        for i, distance in enumerate(result["distances"][0]):
            if distance > (0.97 if self.mode == "lexical" else 0.75):
                continue
            if self.mode == "lexical":
                # Hash buckets can collide: require a real shared token as well.
                query_words = set(re.findall(r"[\w]+", query.lower()))
                document_words = set(re.findall(r"[\w]+", result["documents"][0][i].lower()))
                stopwords = {"i", "a", "the", "is", "and", "or", "to", "my", "me", "for", "with", "please"}
                if not (query_words - stopwords) & document_words:
                    continue
            refs.append(
                {
                    "source_id": result["ids"][0][i],
                    "source_type": "rag_chunk",
                    "excerpt": result["documents"][0][i],
                    "source": result["metadatas"][0][i]["source"],
                    "score": round(1 - distance, 3),
                }
            )
        return refs
