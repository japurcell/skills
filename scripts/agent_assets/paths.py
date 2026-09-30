"""Portable relative path validation shared by catalogs and records."""

from pathlib import PurePosixPath
import re

from .sources import AssetError


def safe_path(value: str) -> str:
    if not isinstance(value, str):
        raise AssetError("ASSET_CATALOG_INVALID", "Catalog paths must be strings.")
    path = PurePosixPath(value)
    reserved = r"^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)"
    if path.is_absolute() or ".." in path.parts or "\\" in value or not path.parts or value != path.as_posix() or any(
        part.endswith((".", " ")) or re.match(reserved, part, re.IGNORECASE) or
        any(ord(c) < 32 or c in '<>:"|?*' for c in part) for part in path.parts
    ):
        raise AssetError("ASSET_CATALOG_INVALID", "Catalog path must be a safe relative path.")
    return path.as_posix()

