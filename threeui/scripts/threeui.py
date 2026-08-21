#!/usr/bin/env python3
"""Search and install verified ThreeUI Community source files."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen


REGISTRY_URL = (
    "https://raw.githubusercontent.com/MengTo/threeui/main/public/source-code.json"
)
ASSET_BASE_URL = "https://raw.githubusercontent.com/MengTo/threeui/main/"


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": "threeui-skill/1"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def load_registry(url=REGISTRY_URL):
    registry = json.loads(fetch_bytes(url))
    if registry.get("schemaVersion") != 1:
        raise ValueError("unsupported registry schema")
    return registry


def safe_path(value):
    path = PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe path {value!r}")
    return Path(*path.parts)


def verify(data, expected, path):
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f"digest mismatch for {path}")


def print_components(components):
    for item in sorted(components, key=lambda component: component["id"]):
        print(f'{item["id"]}\t{item["exportName"]}\t{item["runtime"]}')


def search_components(components, query):
    needle = query.casefold()
    return [
        item
        for item in components
        if needle
        in " ".join(
            (item.get("id", ""), item.get("exportName", ""), item.get("runtime", ""))
        ).casefold()
    ]


def install_component(registry, component_id, target, asset_base, force=False):
    components = registry.get("components", [])
    component = next((item for item in components if item.get("id") == component_id), None)
    if component is None:
        raise ValueError(f"unknown component {component_id!r}")

    shared = {item["path"]: item for item in registry.get("sharedFiles", [])}
    records = list(component.get("files", []))
    for path in component.get("sharedFilePaths", []):
        if path not in shared:
            raise ValueError(f"missing shared file {path!r}")
        records.append(shared[path])

    payloads = {}
    for record in records:
        relative = safe_path(record["path"])
        data = record["code"].encode("utf-8")
        verify(data, record["sha256"], relative)
        if relative in payloads and payloads[relative] != data:
            raise ValueError(f"conflicting source file {relative}")
        payloads[relative] = data

    for asset in component.get("assets", []):
        relative = safe_path(asset["path"])
        url = urljoin(asset_base.rstrip("/") + "/", quote(asset["path"], safe="/"))
        data = fetch_bytes(url)
        verify(data, asset["sha256"], relative)
        payloads[relative] = data

    target = Path(target)
    root = target.resolve()
    for relative in payloads:
        destination = target / relative
        resolved = destination.resolve(strict=False)
        if os.path.commonpath((root, resolved)) != str(root):
            raise ValueError(f"unsafe path {relative}")
        if destination.exists() and not force:
            raise FileExistsError(f"already exists {relative}")

    for relative, data in sorted(payloads.items(), key=lambda item: item[0].as_posix()):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    return sorted(payloads, key=lambda path: path.as_posix())


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--registry-url", default=REGISTRY_URL)
    root.add_argument("--asset-base", default=ASSET_BASE_URL)
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    search = commands.add_parser("search")
    search.add_argument("query")
    install = commands.add_parser("install")
    install.add_argument("component")
    install.add_argument("--target", type=Path, default=Path.cwd())
    install.add_argument("--force", action="store_true")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    registry = load_registry(args.registry_url)
    if args.command == "list":
        print_components(registry["components"])
        return
    if args.command == "search":
        print_components(search_components(registry["components"], args.query))
        return

    written = install_component(
        registry, args.component, args.target, args.asset_base, args.force
    )
    for path in written:
        print(path.as_posix())
    component = next(item for item in registry["components"] if item["id"] == args.component)
    print(component["sourceCommit"])


if __name__ == "__main__":
    main()
