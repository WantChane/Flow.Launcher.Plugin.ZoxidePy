import sys
from pathlib import Path
from typing import List
import subprocess
import re
import os
import logging

from pyflowlauncher import Plugin, Result, send_results
from pyflowlauncher.result import ResultResponse
from pyflowlauncher.api import copy_to_clipboard
from pyflowlauncher.icons import FOLDER, COPY, RECYCLEBIN
from error import *

plugindir = Path.absolute(Path(__file__).parent)
paths = (".", "lib", "plugin")
sys.path = [str(plugindir / p) for p in paths] + sys.path

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ZoxideResult:
    def __init__(self, path: str, score: int):
        self.path = path
        self.score = score

    def __repr__(self):
        return f"ZoxideResult(path={self.path}, score={self.score})"


plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    if query.startswith("cd "):
        return _plugin_query_cd(query[3:].strip())
    else:
        return _plugin_query_open(query)


@plugin.on_method
def open_directory(path: str, zoxide_path: str) -> None:
    if not os.path.exists(path):
        raise DirectoryNotFound(path)

    os.startfile(path)
    _zoxide_add(path, zoxide_path)


@plugin.on_method
def delete_directory(path: str, zoxide_path: str) -> None:
    _zoxide_remove(path, zoxide_path)


@plugin.on_method
def context_menu(data: str) -> ResultResponse:
    return send_results(list(_context_menu_results(data)))


def _get_zoxide_path() -> str:
    zoxide_path = (
        plugin.settings.get("zoxide_path", "zoxide.exe")
        if plugin.settings
        else "zoxide.exe"
    )
    if not _is_executable_available(zoxide_path):
        raise ZoxideNotFound(zoxide_path)
    return zoxide_path


def _is_executable_available(path: str) -> bool:
    import shutil

    if os.path.exists(path):
        return True
    return shutil.which(path) is not None


def _context_menu_results(path: str):
    yield Result(
        Title="Copy path",
        SubTitle=f"Copy {path} to clipboard",
        IcoPath=COPY,
        JsonRPCAction=copy_to_clipboard(path),
    )

    zoxide_path = _get_zoxide_path()
    yield Result(
        Title="Remove from zoxide",
        SubTitle=f"Remove {path} from zoxide database",
        IcoPath=RECYCLEBIN,
        JsonRPCAction={
            "method": "delete_directory",
            "parameters": [path, zoxide_path],
        },
    )


def _zoxide_query(query: str, zoxide_path: str) -> List[ZoxideResult]:
    query_parts = re.split(r"\s+", query.strip())
    cmd = [zoxide_path, "query", "--list", "--score"] + query_parts

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=os.environ.copy(),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    if result.returncode != 0:
        raise ZoxideQueryError(query, result.stderr.strip())

    return _parse_zoxide_output(result.stdout)


def _parse_zoxide_output(output: str) -> List[ZoxideResult]:
    paths = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            score, path = line.strip().split(" ", 1)
            score = int(float(score) * 10)
            paths.append(ZoxideResult(path, score))
        except (ValueError, IndexError) as e:
            raise ZoxideResultParseError(line) from e
    return paths


def _zoxide_add(path: str, zoxide_path: str) -> bool:
    cmd = [zoxide_path, "add", path.strip()]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=os.environ.copy(),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    if result.returncode != 0:
        raise ZoxideAddError(path, result.stderr.strip())
    return True


def _zoxide_remove(path: str, zoxide_path: str) -> bool:
    cmd = [zoxide_path, "remove", path.strip()]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=os.environ.copy(),
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    if result.returncode != 0:
        raise ZoxideRemoveError(path, result.stderr.strip())
    return True


def _plugin_query_open(query: str) -> ResultResponse:
    zoxide_path = _get_zoxide_path()
    if not query.strip():
        return send_results([])
    results = _zoxide_query(query, zoxide_path)
    if not results:
        return send_results([])

    flow_results = []
    for result in results:
        flow_results.append(
            Result(
                Title=Path(result.path).name,
                SubTitle=f"Path: {result.path}",
                IcoPath=FOLDER,
                JsonRPCAction={
                    "method": "open_directory",
                    "parameters": [result.path, zoxide_path],
                },
                Score=result.score,
                ContextData=result.path,
            )
        )
    return send_results(flow_results)


def _plugin_query_cd(query: str) -> ResultResponse:
    zoxide_path = _get_zoxide_path()
    if not query.strip():
        return send_results([])
    if os.path.exists(query) and os.path.isdir(query):
        return send_results(
            [
                Result(
                    Title=query,
                    SubTitle=f"Add this directory to zoxide and open it",
                    IcoPath=FOLDER,
                    JsonRPCAction={
                        "method": "open_directory",
                        "parameters": [query, zoxide_path],
                    },
                )
            ]
        )
    else:
        return send_results(
            [
                Result(
                    Title=f"Invalid directory: {query}",
                    SubTitle="Please provide a valid directory path",
                    IcoPath=FOLDER,
                )
            ]
        )


if __name__ == "__main__":
    plugin.run()
