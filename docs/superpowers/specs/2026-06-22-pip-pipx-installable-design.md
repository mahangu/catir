# Make catir installable via pip / pipx / uvx (git + local)

**Date:** 2026-06-22
**Status:** Approved

## Goal

Make `catir` cleanly installable as a command-line tool from a git URL or a
local checkout, using the standard Python installer ecosystem (`pip`, `pipx`,
`uvx`/`uv tool`). No PyPI publishing.

## Scope decision

- **Install source:** git/local only. No PyPI account, no upload, no CI
  publishing pipeline.
- The existing `setup.py` already technically supports `pipx install git+...`,
  but it uses the legacy `setup.py`-only style and lacks `requires-python`.
  This work modernizes the packaging metadata so the standard tools all work
  cleanly with no warnings.

## Approach

Replace `setup.py` with a single `pyproject.toml` (PEP 621 metadata, setuptools
backend). Chosen over keeping `setup.py` (legacy style) and over a full
src-layout repackage (overkill for one ~260-line module).

Because `pyproject.toml` is the standard metadata format, the same file makes
catir installable by **pip, pipx, and uvx/uv tool** with no tool-specific
configuration.

## Changes

1. **Add `pyproject.toml`:**
   - `[build-system]` → setuptools (`>=61`, for PEP 621 support) + `build_meta`
   - `[project]` → name `catir`, version `0.6`, description, `readme`,
     `requires-python = ">=3.7"` (uses f-strings + `pathlib`),
     `license`, `authors`, `dependencies = ["Pillow"]`
   - `[project.urls]` → Homepage = GitHub repo
   - `[project.scripts]` → `catir = "catir:main"` (same entry point as today)
   - `[tool.setuptools] py-modules = ["catir"]` → single top-level module, not a
     package directory
2. **Delete `setup.py`** — fully superseded; nothing installs catir by name yet,
   so nothing depends on it.
3. **Update `README.md`** — add install/run instructions for pipx, uvx, and
   local pip, plus a one-line usage example.

## Out of scope (not touched)

- The rename logic in `catir.py`
- The stray `import os.path as path` (catir.py line ~213)
- The `deployment_name` derivation behavior

These are pre-existing and unrelated to packaging.

## Verification

In the repo:

```sh
pipx install .            # or: uv tool install .
catir --help              # entry point resolves, Pillow pulls in
pipx uninstall catir      # cleanup
```

Success = `catir --help` prints usage without error after a clean install.

## Net change

+1 file (`pyproject.toml`), −1 file (`setup.py`), README edit.
