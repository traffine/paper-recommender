import json
from typing import Dict, List

import pinecone
from core.config import (
    N_RECOMMEND,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX,
)
from openai import OpenAI


class Pinecone:
    def __init__(self):
        pc = pinecone.Pinecone(
            api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT
        )
        self.index = pc.Index(PINECONE_INDEX)

    def upsert_data(self, vectors: List[Dict]) -> None:
        self.index.upsert(vectors=vectors)

    def query(
        self,
        user_input: str,
        keywords: List[str],
        excluded_ids: List[str],
        top_k: int = N_RECOMMEND,
        include_metadata: bool = True,
    ) -> Dict:
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        user_vector = (
            client.embeddings.create(input=[user_input], model=OPENAI_EMBEDDING_MODEL)
            .data[0]
            .embedding
        )

        query = self.index.query(
            vector=user_vector,
            filter={
                "$and": [
                    {"keywords": {"$in": keywords}},
                    {"id": {"$nin": excluded_ids}},
                ]
            },
            top_k=top_k,
            include_metadata=include_metadata,
        )
        return query


def split_vectors(vectors: List[Dict], num_parts: int) -> List[List[Dict]]:
    avg = len(vectors) // num_parts
    remainder = len(vectors) % num_parts
    splitted_vectors = []
    start = 0
    for i in range(num_parts):
        end = start + avg + (1 if i < remainder else 0)
        splitted_vectors.append(vectors[start:end])
        start = end
    return splitted_vectors


if __name__ == "__main__":
    with open("data/papers/j-stage.json", encoding="utf-8") as f:
        data = json.load(f)

    abstracts = [d["abstract"] for d in data]

    oai_client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    embeddings = oai_client.embeddings.create(
        input=abstracts, model=OPENAI_EMBEDDING_MODEL
    )
    vectors = []
    for i, text in enumerate(embeddings.data):
        vectors.append(
            {
                "id": data[i]["id"],
                "values": embeddings.data[i].embedding,
                "metadata": {
                    "id": data[i]["id"],
                    "title": data[i]["title"],
                    "keywords": data[i]["keywords"],
                    "abstract": data[i]["abstract"],
                    "doi": data[i]["doi"],
                },
            }
        )

    splitted_vectors = split_vectors(vectors=vectors, num_parts=10)

    pc_client = Pinecone()
    for v in splitted_vectors:
        pc_client.upsert_data(vectors=v)
