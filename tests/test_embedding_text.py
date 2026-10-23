# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""The entity description recipe: its exact bytes are a contract."""

from __future__ import annotations

import trellion_protocols as tp
from trellion_protocols.embedding_text import entity_description


def nb(name, typ, rel, direction="outgoing"):
    return {"name": name, "type": typ, "rel_type": rel, "direction": direction}


def test_no_neighbours_is_the_header_alone():
    assert entity_description("python", "language", []) == "python (language)"


def test_neighbours_keep_their_order_and_direction():
    got = entity_description("python", "language", [
        nb("memory leaks", "concept", "CAUSES"),
        nb("ML pipeline", "process", "PART_OF", "incoming"),
    ])
    assert got == ("python (language): CAUSES -> memory leaks (concept), "
                   "PART_OF <- ML pipeline (process)")


def test_any_direction_but_outgoing_reads_incoming():
    assert entity_description("a", "t", [nb("b", "t", "R", "")]) == "a (t): R <- b (t)"


def test_accepts_any_iterable_of_mappings():
    rows = (nb(f"n{i}", "t", "R") for i in range(2))
    assert entity_description("a", "t", rows) == "a (t): R -> n0 (t), R -> n1 (t)"


def test_the_selection_contract_is_exported():
    assert tp.ENTITY_DESCRIPTION_MAX_NEIGHBOURS == 20
    # strongest first, then a total tie-break: the same rows always give the same text
    assert tp.ENTITY_NEIGHBOUR_ORDER_SQL.startswith("COALESCE(e.confidence, 1.0) DESC")
    assert tp.ENTITY_NEIGHBOUR_ORDER_SQL.endswith("n.entity_id")
    assert tp.entity_description is entity_description
