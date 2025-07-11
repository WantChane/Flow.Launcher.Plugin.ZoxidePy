import sys
from pathlib import Path
from typing import List
import subprocess
import re
import os
import logging

from lib.pyflowlauncher import Plugin, Result, send_results
from lib.pyflowlauncher.result import ResultResponse
from lib.pyflowlauncher.api import copy_to_clipboard
from lib.pyflowlauncher.icons import FOLDER, COPY, RECYCLEBIN

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


@plugin.on_method
def open_directory(path: str, zoxide_path: str) -> None:
    if not os.path.exists(path):
        logger.error(f"Path does not exist: {path}")
        return
    try:
        os.startfile(path)
        _zoxide_add(path, zoxide_path)
    except Exception as e:
        logger.error(f"Failed to open directory {path}: {e}")


@plugin.on_method
def delete_directory(path: str, zoxide_path: str) -> None:
    try:
        _zoxide_remove(path, zoxide_path)
    except Exception as e:
        logger.error(f"Failed to delete directory {path}: {e}")


@plugin.on_method
def context_menu(data: str) -> ResultResponse:
    return send_results(list(_context_menu_results(data)))


def _get_zoxide_path() -> str:
    return (
        plugin.settings.get("zoxide_path", "zoxide.exe")
        if plugin.settings
        else "zoxide.exe"
    )


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
    try:
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
            if result.stderr:
                logger.error(
                    "zoxide query failed with code %d: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
            return []

        return _parse_zoxide_output(result.stdout)

    except Exception as e:
        logger.error("Exception in zoxide_query: %s", str(e))
        return []


def _parse_zoxide_output(output: str) -> List[ZoxideResult]:
    paths = []
    for line in output.splitlines():
        if line.strip():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                try:
                    score = int(float(parts[0]) * 10)
                    path = parts[1]
                    paths.append(ZoxideResult(path=path, score=score))
                except ValueError:
                    continue
    return paths


def _zoxide_add(path: str, zoxide_path: str) -> bool:
    try:
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
            if result.stderr:
                logger.error(
                    "zoxide add failed with code %d: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
            return False
        return True

    except Exception as e:
        logger.error("Exception in zoxide_add: %s", str(e))
        return False


def _zoxide_remove(path: str, zoxide_path: str) -> bool:
    try:
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
            if result.stderr:
                logger.error(
                    "zoxide remove failed with code %d: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
            return False
        return True

    except Exception as e:
        logger.error("Exception in zoxide_remove: %s", str(e))
        return False


if __name__ == "__main__":
    plugin.run()
