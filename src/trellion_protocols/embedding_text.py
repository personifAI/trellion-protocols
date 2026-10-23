# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""The text an entity is embedded from.

An entity's vector is the embedding of a one-line description of its graph
neighbourhood. Whoever writes entity vectors and whoever re-embeds them into a
new model (trellion's space migration) must build byte-identical text, or the
re-embedded vector answers a different question than the original. This
module is that one recipe; both sides call it instead of keeping a copy.

Format::

    python (language): CAUSES -> memory leaks (concept), PART_OF <- ML pipeline (process)

The caller selects the neighbours. Both sides must select the same ones, in
the same order: at most :data:`ENTITY_DESCRIPTION_MAX_NEIGHBOURS` edges
touching the entity, ordered by :data:`ENTITY_NEIGHBOUR_ORDER_SQL`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

#: How many neighbours a description names.
ENTITY_DESCRIPTION_MAX_NEIGHBOURS = 20

#: The ORDER BY for the neighbour query, over ``edges e`` joined to the
#: neighbour as ``n`` (``entities``). Strongest edge first (a NULL confidence
#: counts as 1.0); ties broken by relation, neighbour name and neighbour id so
#: two queries over the same rows always name the same neighbours in the same
#: order.
ENTITY_NEIGHBOUR_ORDER_SQL = (
    "COALESCE(e.confidence, 1.0) DESC, e.rel_type, n.canonical_name, n.entity_id"
)


def entity_description(name: str, etype: str, neighbours: Iterable[Mapping[str, str]]) -> str:
    """``name (type)``, then ``: REL -> neighbour (type), ...`` when it has neighbours.

    Each neighbour is a mapping with ``name``, ``type``, ``rel_type`` and
    ``direction`` (``"outgoing"`` when the entity is the edge's source,
    anything else reads as incoming), already in order and already capped.
    """
    header = f"{name} ({etype})"
    parts = []
    for nb in neighbours:
        arrow = "->" if nb["direction"] == "outgoing" else "<-"
        parts.append(f"{nb['rel_type']} {arrow} {nb['name']} ({nb['type']})")
    if not parts:
        return header
    return f"{header}: {', '.join(parts)}"
