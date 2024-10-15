# main.py

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import dotenv

from router import router

import logging
import uuid
from datetime import datetime

dotenv.load_dotenv()

# Set up logging with timestamped filename
filename = f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    filename=filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Request ID: %(request_id)s] - %(message)s',
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
    "http://65.109.96.234",
    "https://65.109.96.234:443",
    "http://65.109.96.234:80"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_unique_id_and_log(request: Request, call_next):
    # Generate unique ID
    request_id = str(uuid.uuid4())
    # Get client IP address
    client_ip = request.client.host if request.client else 'unknown'
    # Create a logger adapter with the request ID
    logger = logging.LoggerAdapter(logging.getLogger(), {'request_id': request_id})

    # Store the logger in the request state
    request.state.logger = logger

    # Log the request
    logger.info(f"Request from IP {client_ip}: {request.method} {request.url.path}")

    # Proceed with the request
    response = await call_next(request)

    # Optionally log the response status code
    logger.info(f"Response: Status code {response.status_code}")
    return response

app.include_router(router=router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
