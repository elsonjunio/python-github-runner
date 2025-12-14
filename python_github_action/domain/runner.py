from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Runner:
    name: str
    path: Path
    repo_url: str
    status: str           # created | running | stopped | error
    pid: Optional[int]
