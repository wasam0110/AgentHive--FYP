"""Persistent Chroma retrieval with explicit lexical-demo or semantic embeddings."""

import hashlib
import math
import re
from datetime import date
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


DOCUMENT_FIELDS = {"language", "review_date", "audience", "review_status"}


def lexical_vector(text):
    """Offline feature-hashing baseline. This is NOT a learned semantic embedding."""
    vector = [0.0] * 384
    for word in re.findall(r"[\w]+", text.lower()):
        index = int(hashlib.sha256(word.encode()).hexdigest()[:8], 16) % len(vector)
        vector[index] += 1
    norm = math.sqrt(sum(v * v for v in vector)) or 1
    return [v / norm for v in vector]


def _document_content(text):
    """Return optional reviewed-document metadata and content without its front matter."""
    if not text.startswith("---\n"):
        return {}, text
    marker = text.find("\n---\n", 4)
    if marker == -1:
        raise ValueError("Document front matter is not closed")
    values = {}
    for line in text[4:marker].splitlines():
        key, separator, value = line.partition(":")
        if not separator or key not in DOCUMENT_FIELDS or not value.strip():
            raise ValueError("Document front matter is malformed")
        if key in values:
            raise ValueError(f"Duplicate document field: {key}")
        values[key] = value.strip()
    if "review_date" in values:
        try:
            date.fromisoformat(values["review_date"])
        except ValueError as exc:
            raise ValueError("Document review_date must be an ISO date") from exc
    if values.get("review_status") == "reviewed" and "review_date" not in values:
        raise ValueError("Reviewed documents require review_date")
    return values, text[marker + 5 :]


def chunk_text(text, size=800, step=650):
    """Yield stable character offsets and bounded chunks for one document."""
    if size <= 0 or step <= 0 or step > size:
        raise ValueError("Chunk size and step must be positive, with step no larger than size")
    return [(offset, text[offset : offset + size]) for offset in range(0, len(text), step)]


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
        """Rebuild the profile index with stable chunks and source-review metadata."""
        paths = sorted(Path(directory).glob("*.md"))
        if not paths:
            raise ValueError(f"No knowledge documents found in {directory}")
        ids, docs, metadata = [], [], []
        for path in paths:
            raw_text = path.read_text(encoding="utf-8")
            fields, text = _document_content(raw_text)
            source_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
            for offset, chunk in chunk_text(text):
                ids.append(f"{path.stem}:{offset}")
                docs.append(chunk)
                metadata.append(
                    {
                        "source": path.name,
                        "source_id": f"{path.stem}:{offset}",
                        "offset": offset,
                        "version": source_hash,
                        "language": fields.get("language", "en"),
                        "review_date": fields.get("review_date"),
                        "audience": fields.get("audience", "customer"),
                        "review_status": fields.get("review_status", "unreviewed"),
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
