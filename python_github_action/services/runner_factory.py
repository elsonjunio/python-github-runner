import json
import subprocess
from pathlib import Path
from python_github_action.config import settings
from python_github_action.infra import filesystem
import shutil


class RunnerFactory:
    def __init__(self):
        self.base_dir = Path(settings.base_runner_dir)
        self.immutable_dir = Path(settings.base_immutable_dir)

    def create(self, name: str, repo_url: str, token: str):

        runner_dir = self.base_dir / name

        if runner_dir.exists():
            raise ValueError('Runner já existe')

        # copia runtime completo
        # self._sync_runner_base(self.immutable_dir, runner_dir)

        # cria diretório do runner
        runner_dir.mkdir(parents=True)
        (runner_dir / '_work').mkdir()

        # copia item a item
        for item in self.immutable_dir.iterdir():
            target = runner_dir / item.name
            #if item.name == 'externals':
            #    target.symlink_to(item)
            #else:
            #    self._sync_runner_base(item, target)


            if item.name == "externals":
                target.symlink_to(item)
                continue

            if item.is_dir():
                shutil.copytree(item, target, symlinks=True)
            else:
                shutil.copy2(item, target)


        # salva metadata mínima
        (runner_dir / 'runner.json').write_text(
            json.dumps(
                {
                    'repo_url': repo_url,
                    'name': name,
                },
                indent=2,
            )
        )

        # registra o runner no GitHub (modo unattended)
        self._register_runner(
            runner_dir=runner_dir,
            repo_url=repo_url,
            token=token,
            name=name,
        )

    def _sync_runner_base(self, src: Path, dst: Path):
        subprocess.run(
            [
                'rsync',
                '-a',
                '--link-dest',
                str(src),
                str(src) + '/',
                str(dst) + '/',
            ],
            check=True,
        )

    def _register_runner(
        self,
        runner_dir: Path,
        repo_url: str,
        token: str,
        name: str,
    ):
        cmd = [
            'bash',
            './config.sh',
            '--url',
            repo_url,
            '--token',
            token,
            '--name',
            name,
            '--work',
            '_work',
            '--unattended',
            '--replace',
            '--disable-sudo',
        ]

        result = subprocess.run(
            cmd,
            cwd=runner_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f'Erro ao registrar runner:\n{result.stdout}')

    def start(self, name: str):
        runner_dir = self.base_dir / name

        if not runner_dir.exists():
            raise ValueError('Runner não existe')

        log_dir = runner_dir / 'logs'
        log_dir.mkdir(exist_ok=True)

        log_file = open(log_dir / 'runner.log', 'a')

        proc = subprocess.Popen(
            ['bash', 'run.sh'],
            cwd=runner_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

        (runner_dir / 'pid').write_text(str(proc.pid))

    def stop(self, name: str):
        runner_dir = self.base_dir / name

        pid = filesystem.find_runner_pid(runner_dir)

        if not pid:
            return

        import os, signal

        os.kill(pid, signal.SIGTERM)

    def delete(self, name: str):
        self.stop(name)
        import shutil

        shutil.rmtree(self.base_dir / name)
