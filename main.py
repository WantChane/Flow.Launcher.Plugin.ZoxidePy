import sys
from pathlib import Path
import os

from pyflowlauncher import Plugin, send_results
from pyflowlauncher.result import ResultResponse
from src.zoxide import Zoxide
from src.error import *

plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path

plugin = Plugin()

zoxide = Zoxide(plugin)


@plugin.on_method
def query(query: str) -> ResultResponse:
    if query.startswith("cd "):
        return zoxide.cd(query[3:])
    else:
        return zoxide.open(query)


@plugin.on_method
def open_directory(path: str) -> None:
    if not os.path.exists(path):
        raise DirectoryNotFound(path)

    os.startfile(path)
    zoxide.zoxide_add(path)


@plugin.on_method
def delete_directory(path: str) -> None:
    zoxide.zoxide_remove(path)


@plugin.on_method
def context_menu(data: str) -> ResultResponse:
    return send_results(zoxide.generate_context_menu(data))


if __name__ == "__main__":
    plugin.run()
