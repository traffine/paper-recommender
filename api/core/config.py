import os

# FastAPI CORS
ALLOW_ORIGINS = [
    # "http://localhost:8080",
    # "http://localhost:8000",
    "*"
]

# FastAPI token
BEARER_TOKEN = "test"

# Environment variable
LOCAL = os.environ.get("LOCAL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
assert OPENAI_API_KEY is not None
assert PINECONE_API_KEY is not None
assert PINECONE_ENVIRONMENT is not None
assert PINECONE_INDEX is not None

# OpenAI config
OPENAI_MODEL = "gpt-4-1106-preview"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_TEMPERATURE = 0.1

# Chat config
RESPONSE_WORD_LIMIT = 75
CONV_HISTORY_COUNT = 30
SUMMARY_WORD_LIMIT = 200
N_KW_STORE = 1
N_RECOMMEND = 3
N_KW_EXTRACT = 2


# DynamoDB table
DYNAMO_CHAT = "paper-recommender-chat"
