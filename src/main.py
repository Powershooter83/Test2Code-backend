# main.py

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import dotenv

from router import router

import logging
import uuid
from datetime import datetime
import os

dotenv.load_dotenv()

# Set up logging with timestamped filename
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
filename = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Custom Formatter to handle missing 'request_id'
class RequestIDFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        return super(RequestIDFormatter, self).format(record)

formatter = RequestIDFormatter(
    '%(asctime)s - %(levelname)s - [Request ID: %(request_id)s] - %(message)s'
)

handler = logging.FileHandler(filename)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

# Configure the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

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
    logger_adapter = logging.LoggerAdapter(logger, {'request_id': request_id})

    # Store the logger in the request state
    request.state.logger = logger_adapter

    # Log the request
    logger_adapter.info(f"Request from IP {client_ip}: {request.method} {request.url.path}")

    # Proceed with the request
    response = await call_next(request)

    # Optionally log the response status code
    logger_adapter.info(f"Response: Status code {response.status_code}")
    return response

app.include_router(router=router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
