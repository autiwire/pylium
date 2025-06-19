from .__impl__ import Manifest
from typing import Dict


def _show_recursive_manifest(manifest: Manifest, simple: bool = False, indent_size = 0, level: int = 0, has_more_siblings: Dict[int, bool] = None):
    if has_more_siblings is None:
        has_more_siblings = {}

    name = "/" if manifest.location is None else manifest.location.fqnShort

    if simple:
        if name != "/":
            print(f"{' ' * indent_size * level}{name}")
    else:
        if level == 0:
            print(f"📦 {name}")
        else:
            prefix_parts = []
            for l in range(level):
                if l == level - 1:
                    connector = "├── " if has_more_siblings.get(level, False) else "└── "
                    prefix_parts.append(connector)
                else:
                    prefix_parts.append("│   " if has_more_siblings.get(l + 1, False) else "    ")

            type_emoji = {
                Manifest.ObjectType.Package: "📦",
                Manifest.ObjectType.Module: "📄",
                Manifest.ObjectType.Class: "❰❱",
                Manifest.ObjectType.Function: "🔹",
                Manifest.ObjectType.Method: "🔸"
            }.get(manifest.objectType, "•")

            print("".join(prefix_parts) + f"{type_emoji} {name}")

    children = manifest.children
    for i, child in enumerate(children):
        has_more = i < len(children) - 1
        next_siblings = has_more_siblings.copy()
        next_siblings[level + 1] = has_more
        _show_recursive_manifest(child, simple, indent_size, level + 1, next_siblings)


def cli_tree(manifest: Manifest, simple: bool = False, indent: int = 0):
    _show_recursive_manifest(manifest, simple, indent)