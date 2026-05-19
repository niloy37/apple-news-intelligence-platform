"""Initialize Neo4j constraints and indexes."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.graph.neo4j_client import Neo4jGraphClient


if __name__ == "__main__":
    client = Neo4jGraphClient()
    client.ensure_constraints()
    client.close()
    print("Neo4j constraints initialized")
