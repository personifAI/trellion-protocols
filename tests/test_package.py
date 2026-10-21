# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

"""The package stays what it says: an interface, standard library only, Apache-2.0.

trellion's own contract tests (in trellion) check that trellion implements
these protocols; this suite checks the package itself.
"""

from __future__ import annotations

import ast
import os
import re
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

import trellion_protocols as tp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "trellion_protocols"
SPDX = re.compile(r"SPDX-License-Identifier:\s*(\S+?)(?:\s*-->)?\s*$")


def _sources() -> list[Path]:
    files = sorted(SRC.glob("*.py"))
    assert len(files) >= 6, f"expected the package sources under {SRC}"
    return files


def test_public_names_resolve_and_version_matches():
    for name in tp.__all__:
        assert getattr(tp, name) is not None, name
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert tp.__version__ == meta["version"]


def test_imports_only_the_standard_library():
    seen = 0
    for path in _sources():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    seen += 1
                    continue
                names = [node.module or ""]
            else:
                continue
            for name in names:
                seen += 1
                top = name.split(".")[0]
                assert top == "__future__" or top in sys.stdlib_module_names, f"{path.name}: {name}"
    assert seen >= 10


def test_no_dependencies_and_apache_metadata():
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert meta["dependencies"] == []
    assert meta["license"] == "Apache-2.0"
    assert meta["license-files"] == ["LICENSE", "NOTICE"]
    assert (ROOT / "LICENSE").read_text().lstrip().startswith("Apache License")
    assert "PersonifAI LLC" in (ROOT / "NOTICE").read_text()


def _tracked_files() -> list[Path]:
    skip_dirs = {".git", ".worktrees", "__pycache__", ".pytest_cache", "dist", "build", ".venv"}
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.endswith(".egg-info")]
        for f in filenames:
            out.append(Path(dirpath) / f)
    return out


def test_every_file_carries_the_apache_spdx_header():
    exempt = {"LICENSE", "NOTICE", "py.typed", ".git"}
    checked = 0
    for path in _tracked_files():
        if path.name in exempt:
            continue
        head = path.read_text().splitlines()[:3]
        ids = [m.group(1) for line in head if (m := SPDX.search(line))]
        assert ids == ["Apache-2.0"], f"{path.relative_to(ROOT)}: SPDX header {ids or 'missing'}"
        checked += 1
    assert checked >= 10


#: The package describes trellion's side of the contract only.
BANNED = re.compile(r"evolve|intel|\btier|licen[cs]|entitle|proprietar", re.I) # leak-ok: the content rule's own pattern


def test_content_describes_only_trellions_side():
    hits = []
    for path in _sources():
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if "SPDX-License-Identifier" in line:
                continue
            if BANNED.search(line):
                hits.append(f"{path.name}:{n}: {line.strip()}")
    assert not hits, "\n".join(hits)


def test_protocols_are_runtime_checkable_and_satisfiable():
    class Host:
        def ssl_verify(self): return True
        def client_cert(self): return None
        def gateway_auth(self): return None
        def gateway_auth_header(self): return {}
        def embed_throttle(self): return None
        embed_unavailable = RuntimeError
        def classify_embed_failure(self, exc): return None
        def llm_throttle(self): return None
        llm_unavailable = RuntimeError
        llm_breaker_open = RuntimeError
        def check_entity(self, name, etype=None): return None
        def drop_tally(self): return None
        async def inc_counter(self, name, value=1, labels=None): return None
        json = None

    assert isinstance(Host(), tp.HostServices)
    assert not isinstance(object(), tp.HostServices)
    assert tp.ADDON_ENTRY_POINT_GROUP == "trellion.addons"


def test_dataclasses_serialise_their_shape():
    h = tp.Hypothesis(path=["a", "b"], description="d", confidence=0.5)
    assert h.to_dict() == {"path": ["a", "b"], "description": "d", "confidence": 0.5, "edges": []}
    snap = tp.TraversalSnapshot("s", "q", None, steps=[tp.TraversalStep("e", "E", "t")])
    assert snap.to_path_json()[0]["entity_id"] == "e"
    ev = tp.Evidence("page", "d", 1, "p", "x", (0, 1), 0.9)
    assert ev.to_dict()["span"] == [0, 1]


def test_schema_constants_are_consistent():
    assert re.fullmatch(r"\d{3}_[a-z_]+", tp.SCHEMA_REV)
    assert tp.TABLES and all(isinstance(c, frozenset) and c for c in tp.TABLES.values())
    assert ":roles" in tp.ROLES_WHERE and "d.metadata" in tp.ROLES_WHERE


@pytest.mark.skipif(not os.environ.get("TP_WHEEL"), reason="TP_WHEEL (a built wheel) not given")
def test_built_wheel_carries_license_and_notice():
    with zipfile.ZipFile(os.environ["TP_WHEEL"]) as z:
        names = z.namelist()
    lic = [n for n in names if n.endswith(".dist-info/licenses/LICENSE")]
    notice = [n for n in names if n.endswith(".dist-info/licenses/NOTICE")]
    assert lic and notice, names
    assert not any(n.startswith("tests/") for n in names)


_PROBE = r"""
import os, sys
events = []
def hook(event, args):
    if event in ("open", "socket.connect", "socket.getaddrinfo", "socket.bind",
                 "subprocess.Popen", "os.system", "urllib.Request", "http.client.connect"):
        # The interpreter's own import machinery reads .py/.pyc files; only
        # opens of anything else count as package I/O.
        if event == "open":
            path = str(args[0])
            if path.endswith((".py", ".pyc")) or "__pycache__" in path or os.path.isdir(path):
                return
        events.append((event, str(args[:1])))

class Env(dict):
    reads = []
    def __getitem__(self, k):
        Env.reads.append(k); return super().__getitem__(k)
    def get(self, k, d=None):
        Env.reads.append(k); return super().get(k, d)
    def __contains__(self, k):
        Env.reads.append(k); return super().__contains__(k)

os.environ = Env(os.environ)
before = set(sys.modules)
sys.addaudithook(hook)
import trellion_protocols, trellion_protocols.addons, trellion_protocols.host
import trellion_protocols.embedding_text, trellion_protocols.schema
import trellion_protocols.stores, trellion_protocols.types
new = sorted(m for m in set(sys.modules) - before if not m.startswith("trellion_protocols"))
print(repr({"events": events, "env": Env.reads, "new_modules": new}))
"""


def test_import_has_no_side_effects():
    """No I/O beyond reading its own modules, no network, no subprocess, no env reads."""
    import ast as _ast
    import subprocess

    env = {k: v for k, v in os.environ.items() if k in ("PATH", "SYSTEMROOT", "HOME")}
    env["PYTHONPATH"] = str(Path(tp.__file__).resolve().parents[1])
    out = subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, %r); " % env["PYTHONPATH"] + _PROBE],
                         capture_output=True, text=True, env=env, check=True).stdout
    got = _ast.literal_eval(out.strip().splitlines()[-1])
    assert got["events"] == [], got["events"]
    assert got["env"] == [], got["env"]
    for mod in got["new_modules"]:
        assert mod.split(".")[0] in sys.stdlib_module_names, f"import pulled in {mod}"


def _leak_scan(tree: Path) -> int:
    import subprocess
    script = Path(__file__).resolve().parent.parent / "scripts" / "leak-scan.sh"
    return subprocess.run(["bash", str(script), str(tree)], capture_output=True).returncode


@pytest.mark.parametrize("value", [
    "github_" + "pat_" + "A1b2" * 8,
    "AGE-SECRET" + "-KEY-1" + "Q" * 20,
])
def test_leak_scan_still_catches_split_prefix_patterns(tmp_path, value):
    (tmp_path / "config.txt").write_text(f"token = {value}\n")
    assert _leak_scan(tmp_path) == 1
    (tmp_path / "config.txt").write_text("token = <redacted>\n")
    assert _leak_scan(tmp_path) == 0
