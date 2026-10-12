# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""Plain data shapes that cross the trellion / add-on boundary.

Dataclasses that trellion and its add-ons both construct or consume, and
TypedDicts describing the rows the store methods in :mod:`.stores` return.
trellion's own modules (``trellion.live.graph_types``, ``trellion.live.video
.types``, ``trellion.live.evidence``) re-export the dataclasses from here, so
there is exactly one class object for each: an instance built on one side is
an instance on the other.

No behaviour beyond serialising a shape back to a dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

# -- graph navigation results -------------------------------------------------


@dataclass
class Hypothesis:
    """A typed hypothesis with confidence derived from graph traversal."""

    path: list[str]
    description: str
    confidence: float
    edges: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "description": self.description,
            "confidence": self.confidence,
            "edges": self.edges,
        }


@dataclass
class GraphResult:
    """Result of a graph navigation pass."""

    seed_entities: list[dict] = field(default_factory=list)
    expanded_entities: list[dict] = field(default_factory=list)
    candidate_page_ids: list[str] = field(default_factory=list)
    reasoning_paths: list[list[dict]] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    entity_name_map: dict[str, str] = field(default_factory=dict)


# -- evidence ------------------------------------------------------------------


@dataclass
class Evidence:
    """A single piece of evidence from the PageIndex."""

    source_type: str  # "page", "chunk", "graph_edge"
    doc_id: str
    page_no: int
    page_id: str
    snippet: str
    span: tuple[int, int]  # character offsets within page_text
    confidence: float  # 0.0 – 1.0

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dictionary."""
        return {
            "source_type": self.source_type,
            "doc_id": self.doc_id,
            "page_no": self.page_no,
            "page_id": self.page_id,
            "snippet": self.snippet,
            "span": list(self.span),
            "confidence": self.confidence,
        }


# -- traversal memory ------------------------------------------------------------


@dataclass
class TraversalStep:
    """One node in a graph walk that became a System 1 record."""

    entity_id: str
    entity_name: str
    entity_type: str
    edge_type: str = ""
    edge_confidence: float = 1.0
    direction: str = "outgoing"  # "seed" | "incoming" | "outgoing"


@dataclass
class TraversalSnapshot:
    """A completed traversal — captured when its outcome score is high enough."""

    snapshot_id: str
    query: str
    query_intent: str | None
    steps: list[TraversalStep] = field(default_factory=list)
    outcome_score: float = 0.0
    timestamp: str | None = None  # ISO-8601 UTC
    persona_id: str = ""
    exploration_rate: float | None = None
    uncertainty_fingerprint: dict | None = None
    query_embedding: list[float] | None = None
    # Who asked: the ACCOUNT of a verified principal, or None for an internal
    # / heartbeat walk. Stored as trellion_traversal_records.user_id.
    user_id: str | None = None
    # Recallable walks (migration 104). Defaults: an unattributed, simulated
    # walk.
    kind: str = "simulated"
    thread_id: str | None = None
    turn_index: int | None = None
    run_id: str | None = None
    provenance: dict | None = None
    evidence: dict | None = None
    usefulness: float | None = None

    def to_path_json(self) -> list[dict]:
        return [
            {
                "entity_id": s.entity_id,
                "entity_name": s.entity_name,
                "entity_type": s.entity_type,
                "edge_type": s.edge_type,
                "edge_confidence": s.edge_confidence,
                "direction": s.direction,
            }
            for s in self.steps
        ]


# -- row shapes returned by the store (documentation types; total=False) --------


class PageRow(TypedDict, total=False):
    page_id: str
    doc_id: str
    page_no: int
    text: str
    meta: dict[str, Any]


class EntityRow(TypedDict, total=False):
    entity_id: str
    canonical_name: str
    type: str
    aliases: list[str]


class EdgeRow(TypedDict, total=False):
    edge_id: str
    src_entity_id: str
    rel_type: str
    dst_entity_id: str
    evidence: Optional[dict[str, Any]]
    evidence_json: Optional[dict[str, Any]]
    confidence: float
    depth: int


class ClusterRow(TypedDict, total=False):
    cluster_id: str
    name: str
    level: int
    parent_cluster_id: Optional[str]
    summary: Optional[str]
    member_count: int
    generation: int
    membership_score: float


class ClusterMemberRow(TypedDict, total=False):
    entity_id: str
    canonical_name: str
    type: str
    aliases: list[str]
    membership_score: float
