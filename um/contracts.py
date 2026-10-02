"""Transport-independent results and errors shared by the SDK, CLI and MCP."""
from dataclasses import asdict, dataclass, field
from typing import Any


class ToolError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class Artifact:
    path: str
    media_type: str
    size: int
    sha256: str
    role: str = "output"


@dataclass
class ErrorInfo:
    code: str
    message: str


@dataclass
class Result:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)
    error: ErrorInfo | None = None

    def to_dict(self) -> dict:
        return asdict(self)
