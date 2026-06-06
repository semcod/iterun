"""ITERUN command-line interface."""

from typing import TYPE_CHECKING

__all__ = ["CLI", "main"]

if TYPE_CHECKING:
    from .main import CLI, main


def __getattr__(name: str):
    if name == "CLI":
        from .main import CLI

        return CLI
    if name == "main":
        from .main import main

        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
