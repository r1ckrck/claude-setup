"""Connector registry. Each module exposes discover(config) and fetch_meta(uri, config)."""

from . import localfs, github, figma, webfetch

REGISTRY = {
    "localfs": localfs,
    "github": github,
    "figma": figma,
    "webfetch": webfetch,
}
