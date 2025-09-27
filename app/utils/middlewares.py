import asyncio
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from starlette.datastructures import FormData, UploadFile
from starlette.types import Message
from werkzeug.datastructures import MultiDict
import secrets
from app.config.main_config import Config
from fastapi_jwt_auth2 import AuthJWT
from app.config.db_connection import get_db
from sqlalchemy.orm import Session
import app.utils.helpers as helpers
from starlette.middleware.base import BaseHTTPMiddleware

security = HTTPBasic()

def authenticate_swagger_ui(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate Swagger UI with Basic Auth"""
    correct_username = secrets.compare_digest(credentials.username, Config.SWAGGER_USER)
    correct_password = secrets.compare_digest(credentials.password, Config.SWAGGER_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

class CheckRevokedTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_db):
        super().__init__(app)
        self.get_db = get_db  # Async database session dependency

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")

        # Use async generator properly
        async for db in self.get_db():  
            if authorization:
                try:
                    # Extract the token from the Authorization header
                    token = authorization.split()[1]
                    auth = AuthJWT()
                    payload = auth.get_raw_jwt(token)  # Extract payload

                    # Check if the token is revoked
                    if await helpers.is_token_revoked(None, payload, db):
                        response = JSONResponse(
                            status_code=401,
                            content={"message": "Token has been revoked! Please log in again."}
                        )
                        response.headers["Access-Control-Allow-Origin"] = "*"
                        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, DELETE, PUT"
                        response.headers["Access-Control-Allow-Headers"] = "*"
                        return response
                except Exception as ex:
                    print(f"Error in token revocation middleware: {str(ex)}")

            response = await call_next(request)
            return response