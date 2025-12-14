from fastapi import APIRouter, HTTPException
from python_github_action.services.runner_factory import RunnerFactory
from python_github_action.infra.filesystem import load_runners
from python_github_action.config import settings
from pathlib import Path

from python_github_action.domain.runner_create import RunnerCreate

router = APIRouter()
factory = RunnerFactory()


@router.get('/')
def list_runners():
    return load_runners(Path(settings.base_runner_dir))


@router.post('/')
def create_runner(payload: RunnerCreate):
    try:
        factory.create(
            name=payload.name,
            repo_url=payload.repo_url,
            token=payload.token,
        )
        return {'status': 'created'}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post('/{name}/start')
def start_runner(name: str):
    factory.start(name)
    return {'status': 'running'}


@router.post('/{name}/stop')
def stop_runner(name: str):
    factory.stop(name)
    return {'status': 'stopped'}


@router.delete('/{name}')
def delete_runner(name: str):
    factory.delete(name)
    return {'status': 'deleted'}
