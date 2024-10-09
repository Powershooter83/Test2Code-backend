import uvicorn
from fastapi import FastAPI
import dotenv

from router import router

dotenv.load_dotenv()
app = FastAPI()
app.include_router(router=router)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)