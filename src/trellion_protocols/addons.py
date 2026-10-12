# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""How trellion finds and loads an add-on.

An add-on declares an entry point in :data:`ADDON_ENTRY_POINT_GROUP` whose
object is an :data:`AddonRegister`: a callable trellion invokes once, at load
time, with its :class:`~trellion_protocols.host.HostServices`. The entry
point's module is the add-on's top-level package; trellion imports the
add-on's other modules from it by name.
"""

from __future__ import annotations

from typing import Callable, Final

from .host import HostServices

#: The entry-point group trellion reads add-ons from.
ADDON_ENTRY_POINT_GROUP: Final[str] = "trellion.addons"

#: An add-on's registration callable.
AddonRegister = Callable[[HostServices], None]
