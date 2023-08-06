from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/current", response_model=UserDb)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    """
    Get the current user's information.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        UserDb: User information.
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Update the user's avatar using Cloudinary.

    Args:
        file (UploadFile): The uploaded image file for the avatar.
        current_user (User): The current authenticated user.
        db (Session): The database session.

    Returns:
        UserAvatarResponse: The updated avatar URL.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
