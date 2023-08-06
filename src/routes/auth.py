from fastapi import APIRouter, Depends, status, Security, HTTPException, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import logging

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail, ResetPasswordRequest
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_password_email


logger = logging.getLogger("fastapi_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs.txt")
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Endpoint for user registration.

    Args:
        body (UserModel): User data from the request.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): The incoming request.
        db (Session): The database session.

    Returns:
        dict: Response containing the newly registered user.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    logger.info(f"User '{new_user.username}' created.")
    return {'user': new_user, 'detail': 'User successfully created. Check your email for confirmation.'}


@router.post("/login", response_model=TokenModel, description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Endpoint for user login.

    Args:
        body (OAuth2PasswordRequestForm): Form data containing username and password.
        db (Session): The database session.

    Returns:
        dict: Response containing access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    logger.info(f"User '{body.username}' logged in successfully.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Endpoint for refreshing access tokens.

    Args:
        credentials (HTTPAuthorizationCredentials): The bearer token.
        db (Session): The database session.

    Returns:
        dict: Response containing new access and refresh tokens.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get('/confirmed_email/{token}', description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Endpoint for confirming a user's email.

    Args:
        token (str): The email confirmation token.
        db (Session): The database session.

    Returns:
        dict: Response confirming the email.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email', description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Endpoint for requesting email confirmation.

    Args:
        body (RequestEmail): Request body containing the user's email.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): The incoming request.
        db (Session): The database session.

    Returns:
        dict: Response indicating that an email has been sent for confirmation.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post('/request_reset_password', dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def request_reset_password(email: str, background_tasks: BackgroundTasks, request: Request,
                                 db: Session = Depends(get_db)):
    """
    Endpoint for requesting a password reset.

    Args:
        email (str): The user's email.
        background_tasks (BackgroundTasks): Background tasks for sending reset password emails.
        request (Request): The incoming request.
        db (Session): The database session.

    Returns:
        dict: Response indicating that a reset password email has been sent.
    """
    exist_user = await repository_users.get_user_by_email(email, db)
    if exist_user:
        token = auth_service.create_reset_password_token(email)
        background_tasks.add_task(send_reset_password_email, exist_user.email, exist_user.username, request.base_url, token)
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )


@router.post('/reset_password', dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def reset_password(reset_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Endpoint for resetting the user's password.

    Args:
        reset_data (ResetPasswordRequest): Request body containing reset data.
        db (Session): The database session.

    Returns:
        dict: Response confirming a successful password reset.
    """
    email = reset_data.email
    token = reset_data.token
    new_password = reset_data.new_password

    payload = auth_service.verify_reset_password_token(token)
    if payload is not None:
        user = repository_users.get_user_by_email(email, db)
        if user:
            hashed_password = auth_service.get_password_hash(new_password)
            await repository_users.update_user_password(email, hashed_password, db)
            return {"message": "Password reset successful"}
        else:
            raise HTTPException(
                status_code=404, detail="User not found"
            )
    else:
        raise HTTPException(
            status_code=400, detail="Invalid token"
        )
