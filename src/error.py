from pyflowlauncher import Result
from pyflowlauncher.icons import ERROR


class ZoxidePyBaseException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_result_response(self):
        return Result(
            Title=self.__class__.__name__,
            SubTitle=self.message,
            IcoPath=ERROR,
        )


class ZoxideNotFound(ZoxidePyBaseException):
    def __init__(self, path: str):
        super().__init__(f"Zoxide not found at path: {path}")


class ZoxideQueryError(ZoxidePyBaseException):
    def __init__(self, query: str, message: str):
        super().__init__(f"Zoxide query failed for '{query}': {message}")


class ZoxideAddError(ZoxidePyBaseException):
    def __init__(self, path: str, message: str):
        super().__init__(f"Failed to add path '{path}' to zoxide: {message}")


class ZoxideRemoveError(ZoxidePyBaseException):
    def __init__(self, path: str, message: str):
        super().__init__(f"Failed to remove path '{path}' from zoxide: {message}")


class ZoxideResultParseError(ZoxidePyBaseException):
    def __init__(self, output: str):
        super().__init__(f"Failed to parse zoxide result: {output}")


class DirectoryNotFound(ZoxidePyBaseException):
    def __init__(self, path: str):
        super().__init__(f"Directory not found: {path}")
