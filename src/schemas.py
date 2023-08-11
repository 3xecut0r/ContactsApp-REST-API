from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field


class ContactModel(BaseModel):
    """
    Pydantic model for creating a contact.

    Attributes:
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (EmailStr): Email of the contact.
        phone (str): Phone number of the contact.
        birthday (date): Birthday of the contact.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(ContactModel):
    """
    Pydantic model for a contact response, including additional attributes.

    Attributes:
        id (int): Contact ID.
        created_at (datetime): Timestamp of contact creation.
        updated_at (datetime): Timestamp of contact update.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class UserModel(BaseModel):
    """
    Pydantic model for user registration.

    Attributes:
        username (str): Username of the user.
        email (EmailStr): Email of the user.
        password (str): Password of the user (6-14 characters).
    """
    username: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=14)


class UserDb(BaseModel):
    """
    Pydantic model for user database representation.

    Attributes:
        id (int): User ID.
        username (str): Username of the user.
        email (EmailStr): Email of the user.
        created_at (datetime): Timestamp of user creation.
        avatar (str): URL of user's avatar.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str

    class ConfigDict:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Pydantic model for user response.

    Attributes:
        user (UserDb): User database representation.
        detail (str): Response detail (default: 'User successfully created').
    """
    user: UserDb
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    """
    Pydantic model for JWT token response.

    Attributes:
        access_token (str): Access token.
        refresh_token (str): Refresh token.
        token_type (str): Token type (default: 'bearer').
    """
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class EmailSchema(BaseModel):
    """
    Pydantic model for email schema.

    Attributes:
        email (EmailStr): Email address.
    """
    email: EmailStr


class RequestEmail(BaseModel):
    """
    Pydantic model for requesting email verification.

    Attributes:
        email (EmailStr): Email address for verification.
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Pydantic model for requesting password reset.

    Attributes:
        email (str): Email address for password reset.
        token (str): Token for password reset.
        new_password (str): New password.
    """
    email: str
    token: str
    new_password: str

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "token": "your_reset_token_here",
                "new_password": "new_secure_password",
            }
        }
