# catir

CAmera Trap Image Renamer (CATIR) — renames camera-trap images to a consistent
timestamp-based format using their EXIF data, for the
[Urban Fishing Cat Conservation Project](https://fishingcats.lk).

Forked from [smart-image-renamer](https://github.com/ronakg/smart-image-renamer).

## Install

Pick whichever tool you use. All install the `catir` command on your PATH.

**pipx**

```sh
pipx install git+https://github.com/mahangu/catir
```

**uv**

```sh
uv tool install git+https://github.com/mahangu/catir
```

**Run once without installing (uvx)**

```sh
uvx --from git+https://github.com/mahangu/catir catir --help
```

**Local checkout (pip)**

```sh
pip install .          # or: pipx install . / uv tool install .
```

## Usage

```sh
catir --help
catir -t /path/to/images        # -t = test mode, shows renames without applying
catir -r /path/to/images        # recurse into subfolders
```
