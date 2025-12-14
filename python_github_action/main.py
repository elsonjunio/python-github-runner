from fastapi import FastAPI
from python_github_action.api.runners import router as runners_router

app = FastAPI(title='GitHub Runner Controller')

app.include_router(runners_router, prefix='/runners')
