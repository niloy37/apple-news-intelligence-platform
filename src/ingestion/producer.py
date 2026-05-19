"""Kafka/Redpanda producer wrapper with a local fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from src.config import Settings, get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PublishedMessage:
    topic: str
    key: str
    value: dict[str, Any]


@dataclass
class EventProducer:
    """Publish normalized records to Redpanda/Kafka when available.

    During local sample runs the class falls back to an in-memory buffer, which
    keeps the project runnable before infrastructure is started.
    """

    settings: Settings = field(default_factory=get_settings)
    _producer: Any | None = None
    published: list[PublishedMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        if os.getenv("KAFKA_DISABLED", "false").lower() == "true":
            logger.info("Kafka producer disabled by KAFKA_DISABLED=true; using in-memory buffer")
            self._producer = None
            return
        try:
            from confluent_kafka import Producer

            self._producer = Producer({"bootstrap.servers": self.settings.redpanda_bootstrap_servers})
        except Exception as exc:  # pragma: no cover - depends on optional runtime service
            logger.info("Kafka producer unavailable, using in-memory fallback: %s", exc)
            self._producer = None

    def publish(self, topic: str, key: str, value: dict[str, Any]) -> None:
        payload = json.dumps(value, default=str).encode("utf-8")
        if self._producer:
            try:
                self._producer.produce(topic, key=key.encode("utf-8"), value=payload)
                self._producer.poll(0)
            except Exception as exc:  # pragma: no cover - optional service
                logger.warning("Kafka publish skipped for %s/%s: %s", topic, key, exc)
        self.published.append(PublishedMessage(topic=topic, key=key, value=value))

    def flush(self) -> None:
        if self._producer:
            self._producer.flush(5)
