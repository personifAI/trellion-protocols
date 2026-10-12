<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 PersonifAI LLC -->

# trellion-protocols

The interface trellion offers to add-ons: `typing.Protocol` definitions for the
stores and host services trellion hands an add-on at load time, the row shapes
those stores return, the names of trellion's tables and columns, the schema
revision (`SCHEMA_REV`), and the entry-point group an add-on registers under.

It contains no implementations. trellion implements these interfaces; an
add-on types against them and receives trellion's objects at run time.

Standard library only, no dependencies. Licensed under Apache-2.0 (see
`LICENSE` and `NOTICE`).
