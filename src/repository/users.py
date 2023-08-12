from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Get a user by their email address.

    Args:
        email (str): Email address of the user.
        db (Session): The database session.

    Returns:
        User: The user with the specified email address.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user.

    Args:
        body (UserModel): The data for the new user.
        db (Session): The database session.

    Returns:
        User: The created user.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update a user's refresh token.

    Args:
        user (User): The user to update.
        token (str | None): The new refresh token or None to clear the token.
        db (Session): The database session.
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Mark a user's email as confirmed.

    Args:
        email (str): The email address to confirm.
        db (Session): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_user_password(email, hashed_password, db: Session) -> None:
    """
    Update a user's password.

    Args:
        email (str): The email address of the user.
        hashed_password (str): The hashed password to set.
        db (Session): The database session.
    """
    user = await get_user_by_email(email, db)
    user.password = hashed_password
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update a user's avatar URL.

    Args:
        email (str): The email address of the user.
        url (str): The new avatar URL.
        db (Session): The database session.

    Returns:
        User: The user with the updated avatar URL.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
