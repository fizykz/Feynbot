"""Collection of non-specific functions and classes."""

import sys
import pathlib
import importlib.util
from types import ModuleType
from typing import Any, Optional


class InvalidKwarg(Exception):
    """Raised when an invalid keyword argument is passed to a function."""

    def __init__(self, kwargs) -> None:
        message = f"Invalid keyword argument(s) passed:\n{kwargs}"
        super().__init__(message)


def check_kwargs(kwargs: dict[str, Any]) -> None:
    if len(kwargs) > 0:
        keys = ", ".join(kwargs.keys())
        raise InvalidKwarg(keys)


def import_from_path(
    path_string: str,
    path: Optional[pathlib.Path] = None,
    name: Optional[str] = None,
) -> ModuleType:
    path = pathlib.Path(path_string).resolve()
    if not name:
        filename = path.name
        parent = path.parent.name
        if filename.endswith(".py"):
            name = parent + "." + filename[:-3]
        else:
            raise ImportError(
                f"Tried to import {path}, but got non-Python file {filename}!"
            )
    premodule = importlib.util.spec_from_file_location(name, path)
    if not premodule:
        raise ImportError(f"Tried importing {path}, but failed!")
    module = importlib.util.module_from_spec(premodule)
    sys.modules["module.name"] = module
    if not (isinstance(module, ModuleType)):
        raise ImportError(f"Tried importing {path}, but failed!")
    if not premodule.loader:
        raise ImportError(f"Tried importing {path}, but failed!")
    premodule.loader.exec_module(module)
    return module
