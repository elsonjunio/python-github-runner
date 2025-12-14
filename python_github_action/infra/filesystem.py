import json
from pathlib import Path
from typing import List
from python_github_action.domain.runner import Runner
import subprocess
from pathlib import Path
from typing import Optional


def load_runners(base_dir: Path) -> List[Runner]:
    runners = []

    for runner_dir in base_dir.iterdir():
        if not runner_dir.is_dir():
            continue

        config_file = runner_dir / 'runner.json'
        if not config_file.exists():
            continue

        data = json.loads(config_file.read_text())

        pid = find_runner_pid(runner_dir)
        status = "running" if pid else "stopped"

        runners.append(
            Runner(
                name=runner_dir.name,
                path=runner_dir,
                repo_url=data['repo_url'],
                status=status,
                pid=pid,
            )
        )

    return runners


def _pid_alive(pid: int) -> bool:
    try:
        import os

        os.kill(pid, 0)
        return True
    except OSError:
        return False


def find_runner_pid(runner_dir: Path) -> Optional[int]:
    """
    Retorna o PID do Runner.Listener executando a partir do runner_dir,
    ou None se não estiver rodando.
    """
    result = subprocess.run(
        ['ps', '-eo', 'pid,args'],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        if 'Runner.Listener' not in line:
            continue

        pid_str, *cmd = line.strip().split(maxsplit=1)
        cmdline = cmd[0] if cmd else ''

        # runner_dir precisa aparecer no command line
        if str(runner_dir) in cmdline:
            return int(pid_str)

    return None
