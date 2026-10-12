# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""The store interfaces an add-on is handed, as ``typing.Protocol``.

trellion implements them (``PageIndexStore``, ``WalkStore``, the traversal
archiver); its contract tests check that every member named here exists on
the concrete class with the same parameters. An add-on types against these
and never imports trellion.

The engine is typed ``Any`` on purpose: naming SQLAlchemy's ``AsyncEngine``
would make this package depend on SQLAlchemy. It is an
``sqlalchemy.ext.asyncio.AsyncEngine`` whose connections have
``search_path`` set to trellion's schema.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol, Sequence, runtime_checkable

from .types import TraversalSnapshot


@runtime_checkable
class WalkStore(Protocol):
    """Reader/maintainer of recallable walks (``trellion_traversal_records``)."""

    async def recall_candidates(
        self,
        user_id: str | None,
        query_embedding: Sequence[float],
        *,
        kind: str = "thread",
        top_k: int = 10,
        persona_id: str | None = None,
    ) -> list[dict[str, Any]]: ...

    async def touch_recalled(
        self, walk_ids: Sequence[str], *, user_id: str | None = None
    ) -> int: ...

    async def mark_stale(
        self, walk_ids: Sequence[str], *, user_id: str | None = None
    ) -> int: ...


@runtime_checkable
class GraphReader(Protocol):
    """The read-only slice of the graph store used to walk the graph."""

    async def search_entities(self, name_pattern: str) -> list[dict]: ...

    async def get_entities_by_ids(self, entity_ids: list[str]) -> dict[str, dict]: ...

    async def get_entity_neighbors(
        self,
        entity_id: str,
        rel_types: Optional[list[str]] = None,
        hops: int = 1,
    ) -> list[dict]: ...

    async def get_neighbors_batch(self, entity_ids: list[str]) -> list[dict]: ...

    async def get_entity_pages_batch(self, entity_ids: list[str]) -> list[str]: ...

    async def get_entity_clusters(self, entity_id: str) -> list[dict]: ...

    async def get_cluster_members(self, cluster_id: str, limit: int = 200) -> list[dict]: ...


@runtime_checkable
class GraphStore(GraphReader, Protocol):
    """The full PageIndex + graph store trellion hands an add-on."""

    #: Knowledge-base audience predicate over ``docs d`` (see ``schema.ROLES_WHERE``).
    ROLES_WHERE: str

    @property
    def engine(self) -> Any:
        """The store's ``AsyncEngine`` (search_path pinned to trellion's schema)."""
        ...

    @property
    def walk_store(self) -> WalkStore:
        """A :class:`WalkStore` over the same engine."""
        ...

    def vec(self, values: list[float]) -> str:
        """Format a float list as a pgvector literal, validating its dimension."""
        ...

    # pages
    async def get_page(self, page_id: str) -> Optional[dict]: ...

    async def get_doc_pages(self, doc_id: str) -> list[dict]: ...

    # entities and edges
    async def upsert_entity(
        self,
        canonical_name: str,
        type: str,
        aliases: Optional[list[str]] = None,
    ) -> str: ...

    async def list_entities(self, limit: int = 500) -> list[dict]: ...

    async def insert_edge(
        self,
        src_entity_id: str,
        rel_type: str,
        dst_entity_id: str,
        evidence: Optional[dict] = None,
        reinforce_factor: float = 0.2,
    ) -> str: ...

    async def export_all_edges(self) -> list[dict]: ...

    async def get_unclassified_edges(self, limit: int = 50) -> list[dict]: ...

    async def update_edge_classification(
        self,
        edge_id: str,
        rel_type: str,
        confidence: float,
        classifier_model: str,
    ) -> None: ...

    # entity embeddings
    async def upsert_entity_embedding(
        self,
        entity_id: str,
        embedding: list[float],
        generation: int,
    ) -> None: ...

    async def get_stale_entity_embeddings(
        self,
        current_generation: int,
        limit: int = 100,
    ) -> list[dict]: ...

    # clusters
    async def upsert_cluster(
        self,
        cluster_id: str,
        name: str,
        level: int,
        parent_id: Optional[str],
        summary: Optional[str],
        centroid: Optional[list[float]],
        member_count: int,
        generation: int,
    ) -> None: ...

    async def set_cluster_members(self, cluster_id: str, members: list[dict]) -> None: ...

    async def delete_clusters(self, generation_below: Optional[int] = None) -> int: ...


@runtime_checkable
class TraversalArchiver(Protocol):
    """Where a captured traversal is handed for archiving."""

    def capture(self, snapshot: TraversalSnapshot) -> Any: ...
