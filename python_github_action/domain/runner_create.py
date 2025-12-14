from dataclasses import dataclass


@dataclass
class RunnerCreate:
    name: str
    repo_url: str
    token: str
