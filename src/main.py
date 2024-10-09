import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import dotenv

from router import router

dotenv.load_dotenv()


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)