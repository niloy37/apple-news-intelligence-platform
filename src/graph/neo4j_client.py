"""Neo4j client wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.config import Settings, get_settings
from src.graph.cypher_constraints import CONSTRAINTS
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Neo4jGraphClient:
    settings: Settings = field(default_factory=get_settings)
    driver: Any | None = None

    def __post_init__(self) -> None:
        try:
            from neo4j import GraphDatabase

            self.driver = GraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password),
                connection_timeout=3,
            )
            self.driver.verify_connectivity()
        except Exception as exc:  # pragma: no cover - optional service
            logger.warning("Neo4j driver unavailable: %s", exc)
            self.driver = None

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def run(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not self.driver:
            logger.info("Neo4j not available; skipped query: %s", cypher[:100])
            return []
        try:
            with self.driver.session() as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        except Exception as exc:  # pragma: no cover - optional service
            logger.warning("Neo4j query skipped after connection failure: %s", exc)
            return []

    def ensure_constraints(self) -> None:
        for statement in CONSTRAINTS:
            self.run(statement)
