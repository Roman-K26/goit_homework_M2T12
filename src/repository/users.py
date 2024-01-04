from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by their email from the database.

    Parameters:
        email (str): The email of the user to retrieve.
        db (Session): The database session.

    Returns:
        User: The user with the specified email.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    Parameters:
        body (UserModel): The user data for the new user.
        db (Session): The database session.

    Returns:
        User: The newly created user.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a user in the database.

    Parameters:
        user (User): The user for whom to update the refresh token.
        token (str | None): The new refresh token.
        db (Session): The database session.
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    Marks a user's email as confirmed in the database.

    Parameters:
        email (str): The email of the user to confirm.
        db (Session): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()