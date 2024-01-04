from typing import Optional
import pickle

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    """
    Class handling authentication-related operations, such as password hashing, token generation, and user validation.

    Attributes:
        pwd_context (CryptContext): Password hashing context.
        SECRET_KEY (str): Secret key for token encoding and decoding.
        ALGORITHM (str): Token encoding algorithm.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme.
        r (Redis): Redis instance for caching user information.

    Methods:
        verify_password(plain_password, hashed_password): Verifies a plain password against a hashed password.
        get_password_hash(password: str): Hashes a password using the configured context.
        create_access_token(data: dict, expires_delta: Optional[float] = None): Generates a new access token.
        create_refresh_token(data: dict, expires_delta: Optional[float] = None): Generates a new refresh token.
        decode_refresh_token(refresh_token: str): Decodes and validates a refresh token, returning the associated email.
        get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): Retrieves the current user
        based on the provided JWT token.
        create_email_token(data: dict): Generates a token for email verification.
        get_email_from_token(token: str): Retrieves the email from an email verification token.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
                Verifies a plain password against a hashed password.

                Args:
                    plain_password (str): The plain password to be verified.
                    hashed_password (str): The hashed password against which to verify.

                Returns:
                    bool: True if the password is valid, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
                Hashes a password using the configured context.

                Args:
                    password (str): The password to be hashed.

                Returns:
                    str: The hashed password.
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
                Generates a new access token.

                Args:
                    data (dict): User data to be included in the token.
                    expires_delta (float, optional): Token expiration time in seconds.

                Returns:
                    str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
                Generates a new refresh token.

                Args:
                    data (dict): User data to be included in the token.
                    expires_delta (float, optional): Token expiration time in seconds.

                Returns:
                    str: The encoded refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
                Decodes and validates a refresh token, returning the associated email.

                Args:
                    refresh_token (str): The refresh token to be decoded.

                Returns:
                    str: The email associated with the refresh token.

                Raises:
                    HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
                Retrieves the current user based on the provided JWT token.

                Args:
                    token (str): The JWT token.
                    db (Session): The database session.

                Returns:
                    User: The current user.

                Raises:
                    HTTPException: If the token is invalid or the user cannot be retrieved.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user


    def create_email_token(self, data: dict):
        """
                Generates a token for email verification.

                Args:
                    data (dict): User data to be included in the token.

                Returns:
                    str: The encoded email verification token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
                Retrieves the email from an email verification token.

                Args:
                    token (str): The email verification token.

                Returns:
                    str: The email associated with the token.

                Raises:
                    HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

auth_service = Auth()
