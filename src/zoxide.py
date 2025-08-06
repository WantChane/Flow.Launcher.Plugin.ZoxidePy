import os
from pathlib import Path
import re
import subprocess
from typing import List

from pyflowlauncher import Result, ResultResponse, send_results
from pyflowlauncher.api import copy_to_clipboard, open_url
from pyflowlauncher.icons import COPY, FOLDER, RECYCLEBIN, WEB_SEARCH
from src.error import (
    ZoxideAddError,
    ZoxideQueryError,
    ZoxideRemoveError,
    ZoxideResultParseError,
)
from src.type import ZoxideResult


class Zoxide:
    def __init__(self, plugin) -> None:
        self.zoxide_path = self._get_zoxide_path(plugin)

    def _get_zoxide_path(self, plugin) -> str:
        import shutil

        zoxide_path = (
            plugin.settings.get("zoxide_path", "zoxide.exe")
            if plugin.settings
            else "zoxide.exe"
        )
        if os.path.exists(zoxide_path) or shutil.which(zoxide_path) is not None:
            return zoxide_path
        else:
            return ""

    def _get_zoxide_not_found_result(self) -> Result:
        return Result(
            Title="Zoxide not found",
            SubTitle="Download and install zoxide",
            IcoPath=WEB_SEARCH,
            JsonRPCAction=open_url("https://github.com/ajeetdsouza/zoxide"),
        )

    def zoxide_add(self, path: str) -> bool:
        cmd = [self.zoxide_path, "add", path.strip()]
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

    def zoxide_query(self, query: str) -> List[ZoxideResult]:
        query_parts = re.split(r"\s+", query.strip())
        cmd = [self.zoxide_path, "query", "--list", "--score"] + query_parts
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
        paths = []
        for line in result.stdout.splitlines():
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

    def zoxide_remove(self, path: str) -> bool:
        cmd = [self.zoxide_path, "remove", path.strip()]
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

    def generate_context_menu(self, path: str) -> List[Result]:
        results = []
        results.append(
            Result(
                Title="Copy path",
                SubTitle=f"Copy {path} to clipboard",
                IcoPath=COPY,
                JsonRPCAction=copy_to_clipboard(path),
            )
        )

        results.append(
            Result(
                Title="Remove from zoxide",
                SubTitle=f"Remove {path} from zoxide database",
                IcoPath=RECYCLEBIN,
                JsonRPCAction={
                    "method": "delete_directory",
                    "parameters": [path],
                },
            )
        )
        return results

    def cd(self, query: str) -> ResultResponse:
        if not self.zoxide_path:
            return send_results([self._get_zoxide_not_found_result()])
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
                            "parameters": [query],
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

    def open(self, query: str) -> ResultResponse:
        if not self.zoxide_path:
            return send_results([self._get_zoxide_not_found_result()])
        if not query.strip():
            return send_results([])

        results = self.zoxide_query(query)
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
                        "parameters": [result.path],
                    },
                    Score=result.score,
                    ContextData=result.path,
                )
            )
        return send_results(flow_results)
