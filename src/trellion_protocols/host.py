# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""Host services: what trellion lends an add-on at load time.

trellion runs its outbound calls through process-wide machinery — TLS
settings, the gateway credential, the embedding throttle, the per-model LLM
throttle and breaker, the entity quality gate, the metrics counter, the JSON
codec. An add-on loaded into the same process must use the SAME instances
(one throttle, one breaker, one credential), not copies. trellion hands an
object satisfying :class:`HostServices` to the add-on's registration callable
(see :mod:`.addons`); every member delegates to trellion's own singletons.

Interfaces only. trellion's contract tests check its implementation against
every member here.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class JsonCodec(Protocol):
    """trellion's JSON codec (the same one its own code uses)."""

    JSONDecodeError: type[Exception]

    def loads(self, data: str | bytes) -> Any: ...

    def dumps(self, obj: Any, **kw: Any) -> str: ...


@runtime_checkable
class EmbedThrottle(Protocol):
    """The process-wide embedding throttle: one concurrency bound, adaptive batch."""

    batch_size: int
    batch_max: int
    consecutive_failures: int

    def effective_batch(self, requested: int) -> int: ...

    def cooldown_s(self) -> float: ...

    async def call(
        self,
        fn: Callable[[], Awaitable[Any]],
        *,
        what: str,
        count: int,
        max_attempts: int | None = None,
        bounded: bool = True,
    ) -> Any: ...


@runtime_checkable
class LLMThrottle(Protocol):
    """The process-wide LLM throttle with a per-model breaker."""

    def blocked_for(self, model: str) -> float | None: ...

    def defer(self, model: str, n: int = 1) -> None: ...

    async def call(
        self,
        model: str,
        fn: Callable[[], Awaitable[Any]],
        *,
        what: str,
        max_attempts: int | None = None,
        bounded: bool = True,
    ) -> Any: ...


@runtime_checkable
class DropTally(Protocol):
    """Counts entity names the quality gate dropped, by reason."""

    def add(self, name: object, reason: str) -> None: ...

    @property
    def total(self) -> int: ...

    def log(self, event: str, **ctx: object) -> None: ...


@runtime_checkable
class HostServices(Protocol):
    """The runtime services trellion lends an add-on. Same instances as trellion's own."""

    # -- transport -----------------------------------------------------------

    def ssl_verify(self) -> Any:
        """The ``verify=`` value for an HTTP client to cluster-internal endpoints."""
        ...

    def client_cert(self) -> Optional[tuple[str, str]]:
        """``(cert_path, key_path)`` for mTLS, or None when none is configured."""
        ...

    def gateway_auth(self) -> Any:
        """An ``httpx.Auth`` presenting this process's gateway credential."""
        ...

    def gateway_auth_header(self) -> dict[str, str]:
        """The gateway credential as request headers, for clients that take headers."""
        ...

    # -- throttles -------------------------------------------------------------

    def embed_throttle(self) -> EmbedThrottle:
        """The process-wide embedding throttle."""
        ...

    @property
    def embed_unavailable(self) -> type[Exception]:
        """Raised by :meth:`EmbedThrottle.call` when the embedder is unavailable."""
        ...

    def classify_embed_failure(self, exc: BaseException) -> Optional[str]:
        """Why an embedding call failed, as a short reason, or None if not retryable."""
        ...

    def llm_throttle(self) -> LLMThrottle:
        """The process-wide LLM throttle and per-model breaker."""
        ...

    @property
    def llm_unavailable(self) -> type[Exception]:
        """Raised by :meth:`LLMThrottle.call` when the model is unavailable."""
        ...

    @property
    def llm_breaker_open(self) -> type[Exception]:
        """The :attr:`llm_unavailable` subclass raised while a model's breaker is open."""
        ...

    # -- entity quality ----------------------------------------------------------

    def check_entity(self, name: object, etype: Optional[str] = None) -> Optional[str]:
        """Why an entity name is junk under trellion's quality gate, or None if it is fine."""
        ...

    def drop_tally(self) -> DropTally:
        """A fresh tally for the names one pass drops."""
        ...

    # -- observability and encoding --------------------------------------------

    async def inc_counter(
        self, name: str, value: int = 1, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a metrics counter through trellion's metrics path."""
        ...

    @property
    def json(self) -> JsonCodec:
        """trellion's JSON codec."""
        ...
