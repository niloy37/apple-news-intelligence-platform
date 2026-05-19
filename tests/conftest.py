import os

os.environ.setdefault("EMBEDDING_PROVIDER", "hash")
os.environ.setdefault("QDRANT_URL", "memory://local")
os.environ.setdefault("SKIP_GRAPH_LOAD", "true")
os.environ.setdefault("SKIP_VECTOR_INDEX", "true")
