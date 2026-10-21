# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""The schema contract: revision, where it is recorded, table and column names.

trellion owns the schema (its Alembic chain under
``src/trellion/db/migrations``). An add-on that reads or writes these tables
does so against THIS description, never against trellion's models.

* :data:`SCHEMA_REV` is the head revision of that chain. trellion's
  contract tests fail when a migration is added and this is not bumped.
* :data:`TABLES` lists, per table, every column the migrations create. The
  database-backed contract test holds it equal to a freshly migrated
  database.
"""

from __future__ import annotations

from typing import Final, Mapping

#: Head of trellion's Alembic chain. Bump with every migration.
SCHEMA_REV: Final[str] = "106_embedding_provenance"

#: Alembic's version table for the trellion chain, and the schema it lives in.
VERSION_TABLE: Final[str] = "alembic_version_memory"
#: Environment variable naming the Postgres schema trellion's tables live in.
SCHEMA_ENV: Final[str] = "NOO_TRELLION_SCHEMA"
#: Its default.
DEFAULT_SCHEMA: Final[str] = "trellion"

# -- table names -------------------------------------------------------------

DOCS: Final = "docs"
PAGES: Final = "pages"
ENTITIES: Final = "entities"
MENTIONS: Final = "mentions"
EDGES: Final = "edges"
ENTITY_EMBEDDINGS: Final = "entity_embeddings"
ENTITY_CLUSTERS: Final = "entity_clusters"
ENTITY_CLUSTER_MEMBERS: Final = "entity_cluster_members"
ENTITY_GRAPH_SIGNALS: Final = "entity_graph_signals"
ENTITIES_TYPED: Final = "noo_entities_typed"
TEMPORAL_EDGES: Final = "noo_temporal_edges"
TRAVERSAL_RECORDS: Final = "trellion_traversal_records"
EPISODES: Final = "trellion_episodes"

#: Every column of every table an add-on may touch, as the migrations create it.
TABLES: Final[Mapping[str, frozenset[str]]] = {
    DOCS: frozenset({
        "doc_id", "source_uri", "title", "hash", "created_at", "metadata",
        "held_at", "hold_reason",
    }),
    PAGES: frozenset({
        "page_id", "doc_id", "page_no", "text", "meta_json", "last_accessed_at",
        "extracted_at", "extraction_claimed_at",
    }),
    ENTITIES: frozenset({
        "entity_id", "canonical_name", "type", "aliases_json", "created_at",
        "user_id", "org_id",
    }),
    MENTIONS: frozenset({"mention_id", "entity_id", "page_id", "span_json", "quote"}),
    EDGES: frozenset({
        "edge_id", "src_entity_id", "rel_type", "dst_entity_id", "evidence_json",
        "created_at", "confidence", "classified_at", "classifier_model", "user_id",
        "org_id",
    }),
    ENTITY_EMBEDDINGS: frozenset({
        "entity_id", "embedding", "computed_at", "generation", "embedding_model",
        "embedding_dim", "embedding_next", "embedding_next_model",
    }),
    ENTITY_CLUSTERS: frozenset({
        "cluster_id", "name", "level", "parent_cluster_id", "summary", "centroid",
        "member_count", "computed_at", "generation", "embedding_model", "embedding_dim",
        "embedding_next", "embedding_next_model",
    }),
    ENTITY_CLUSTER_MEMBERS: frozenset({"entity_id", "cluster_id", "membership_score"}),
    ENTITY_GRAPH_SIGNALS: frozenset({
        "entity_id", "pagerank", "betweenness", "clustering_coeff", "in_degree",
        "out_degree", "triangle_count", "motif_type", "spectral_embedding",
        "propagated_type", "propagated_type_confidence", "signal_generation",
        "computed_at",
    }),
    ENTITIES_TYPED: frozenset({
        "id", "type", "canonical_name", "metadata", "created_at", "user_id", "org_id",
    }),
    TEMPORAL_EDGES: frozenset({
        "id", "subject_id", "predicate", "object_entity_id", "object_value",
        "valid_from", "valid_to", "observed_at", "confidence", "source_entry_id",
        "source_page_id", "source_cycle_id", "metadata", "user_id", "org_id",
    }),
    TRAVERSAL_RECORDS: frozenset({
        "id", "persona_id", "query_text", "query_embedding", "intent",
        "traversal_path", "outcome_score", "exploration_rate",
        "uncertainty_fingerprint", "archived_to_video", "video_frame_id",
        "created_at", "updated_at", "user_id", "org_id", "kind", "thread_id",
        "turn_index", "run_id", "provenance", "evidence", "usefulness", "status",
        "last_validated_at", "last_recalled_at", "recall_count", "expires_at",
        "embedding_model", "embedding_dim", "embedding_next", "embedding_next_model",
    }),
    EPISODES: frozenset({
        "id", "persona_id", "record_type", "index_name", "content_summary",
        "prominence_score", "access_count", "first_accessed_at", "last_accessed_at",
        "avg_search_score", "is_tombstoned", "metadata", "created_at", "updated_at",
        "embedding", "user_id", "embedding_model", "embedding_dim", "embedding_next",
        "embedding_next_model",
    }),
}

#: The knowledge-base audience predicate over ``docs`` (alias ``d``, bind
#: parameter ``:roles``, a text array). A document is readable when its
#: ``metadata.roles`` overlaps the caller's role set; an untagged document only
#: when the set carries the generic ``user`` role. trellion's
#: ``PageIndexStore.ROLES_WHERE`` IS this string.
ROLES_WHERE: Final[str] = """
        ( (jsonb_exists(COALESCE(d.metadata, '{}'::jsonb), 'roles')
           AND jsonb_exists_any(d.metadata->'roles', CAST(:roles AS text[])))
          OR (NOT jsonb_exists(COALESCE(d.metadata, '{}'::jsonb), 'roles')
              AND 'user' = ANY(CAST(:roles AS text[]))) )
    """
