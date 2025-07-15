class ZoxideResult:
    def __init__(self, path: str, score: int) -> None:
        self.path = path
        self.score = score

    def __repr__(self) -> str:
        return f"ZoxideResult(path={self.path}, score={self.score})"
