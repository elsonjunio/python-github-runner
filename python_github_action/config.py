from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_runner_dir: str = '/opt/github-runners'
    base_immutable_dir: str = '/opt/github-runner-base'

    class Config:
        env_file = '.env'


settings = Settings()
