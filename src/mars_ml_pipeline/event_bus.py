from __future__ import annotations

from typing import Protocol

import requests

from mars_ml_pipeline.schemas import PublishedEvent


class EventPublisher(Protocol):
    def publish(self, event: PublishedEvent) -> None:
        """Publish an event to the MARS event bus."""


class NoopPublisher:
    def publish(self, event: PublishedEvent) -> None:
        return None


class InMemoryPublisher:
    def __init__(self) -> None:
        self.events: list[PublishedEvent] = []

    def publish(self, event: PublishedEvent) -> None:
        self.events.append(event)


class HttpEventPublisher:
    def __init__(self, url: str, timeout_seconds: float = 2.0) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def publish(self, event: PublishedEvent) -> None:
        response = requests.post(
            self.url,
            json=event.model_dump(mode="json"),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
