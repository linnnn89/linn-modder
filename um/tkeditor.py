"""Compatibility import for the Heroes' Vow editor; use um.editors.heroes_vow."""
import sys

from um.editors.heroes_vow import tkeditor as _implementation

# Keep one module object for existing Python callers and patch/inspection tools.
sys.modules[__name__] = _implementation
