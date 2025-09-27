from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth2.exceptions import AuthJWTException

def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    error_messages = {
        "missing authorization header": "Missing Authorization Header.",
        "token is invalid": "Token is invalid! Please log in again.",
        "token has expired": "Token has expired! Please log in again.",
        "signature has expired": "Token signature has expired! Please log in again.",
        "token has been revoked": "User already logged out! Please log in again.",
    }
    # Normalize error message to lowercase for comparison
    error_message = error_messages.get(exc.message.lower(), exc.message)

    response = JSONResponse(status_code=401, content={"message": error_message})
    response.headers["Access-Control-Allow-Origin"] = "*"  # Modify for security
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, DELETE, PUT"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response
