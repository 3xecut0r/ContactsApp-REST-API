from pathlib import Path

from fastapi import FastAPI, status, Request, BackgroundTasks, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import uvicorn
import redis.asyncio as redis

from src.conf.config import settings
from src.routes import contacts
from src.routes import auth
from src.routes import users
from src.schemas import EmailSchema


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="REST API",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'src' / 'templates',
)

origins = [
    "http://localhost:3000"
    ]

# Initialize FastAPI app
app = FastAPI()
app.include_router(auth.router, prefix="/api")
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Connect to Redis and initialize FastAPILimiter
@app.on_event("startup")
async def startup():
    """
    Executed on app startup to connect to Redis and initialize FastAPILimiter.
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


# Define root endpoint
@app.get('/', description='No more than 10 requests per minute',
         dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def read_root(request: Request):
    """
    Handler for the root path.

    :param request: The HTTP request.
    :type request: Request
    :return: A dictionary containing the request information.
    :rtype: dict
    """
    return {"request": request}


# Define email sending endpoint
@app.post("/send-email", description='No more than 10 requests per minute',
          dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    """
    Sends an email in the background.

    :param background_tasks: Background tasks to run.
    :type background_tasks: BackgroundTasks
    :param body: The email data.
    :type body: EmailSchema
    :return: A message indicating the email has been sent.
    :rtype: dict
    """
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[body.email],
        template_body={"fullname": "Billy Jones"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="example_email.html")

    return {"message": "email has been sent"}


# Exception handlers

@app.exception_handler(ValidationError)
def validation_error_handler():
    """
    Handles validation errors. Returns a JSON response with an error message for invalid input data.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Invalid input data"}
    )


@app.exception_handler(HTTPException)
def http_exception_handler(exc: HTTPException):
    """
    Handles HTTP exceptions. Returns a JSON response with the exception detail and status code.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(Exception)
def unexpected_exception_handler():
    """
    Handles unexpected exceptions. Returns a JSON response with a generic error message and status code.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
