# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""trellion_protocols — the interface trellion offers to add-ons.

``typing.Protocol`` definitions for the stores and host services trellion
hands an add-on at load time, the row shapes those stores return, trellion's
table and column names, the schema revision, and the entry-point group an
add-on registers under. Nothing here does anything: trellion implements it,
an add-on types against it. The one exception is :mod:`.embedding_text`, the
text recipe both sides must build identically.
"""

from __future__ import annotations

from .addons import ADDON_ENTRY_POINT_GROUP, AddonRegister
from .embedding_text import (
    ENTITY_DESCRIPTION_MAX_NEIGHBOURS,
    ENTITY_NEIGHBOUR_ORDER_SQL,
    entity_description,
)
from .host import DropTally, EmbedThrottle, HostServices, JsonCodec, LLMThrottle
from .schema import (
    DEFAULT_SCHEMA,
    ROLES_WHERE,
    SCHEMA_ENV,
    SCHEMA_REV,
    TABLES,
    VERSION_TABLE,
)
from .stores import GraphReader, GraphStore, TraversalArchiver, WalkStore
from .types import (
    ClusterMemberRow,
    ClusterRow,
    EdgeRow,
    EntityRow,
    Evidence,
    GraphResult,
    Hypothesis,
    PageRow,
    TraversalSnapshot,
    TraversalStep,
)

__version__ = "0.2.0"

__all__ = [
    "ADDON_ENTRY_POINT_GROUP",
    "DEFAULT_SCHEMA",
    "ENTITY_DESCRIPTION_MAX_NEIGHBOURS",
    "ENTITY_NEIGHBOUR_ORDER_SQL",
    "ROLES_WHERE",
    "SCHEMA_ENV",
    "SCHEMA_REV",
    "TABLES",
    "VERSION_TABLE",
    "AddonRegister",
    "ClusterMemberRow",
    "ClusterRow",
    "DropTally",
    "EdgeRow",
    "EmbedThrottle",
    "EntityRow",
    "Evidence",
    "GraphReader",
    "GraphResult",
    "GraphStore",
    "HostServices",
    "Hypothesis",
    "JsonCodec",
    "LLMThrottle",
    "PageRow",
    "TraversalArchiver",
    "TraversalSnapshot",
    "TraversalStep",
    "WalkStore",
    "entity_description",
]
