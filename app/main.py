from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from fastapi.middleware.cors import CORSMiddleware
from app.config.swagger_config import swagger_config, custom_openapi
from app.utils.exceptions import authjwt_exception_handler
from app.config.db_connection import get_db
from app.utils.middlewares import authenticate_swagger_ui, CheckRevokedTokenMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.main_config import Config
# routers admin
from app.routers.admin import auth_router as admin_auth_router
from app.routers.admin import role_permission_router
from app.routers.admin import existing_api_router
# routers front


app = FastAPI(
    docs_url=None,  # Disable the default Swagger UI endpoint
    redoc_url=None,  # Disable the default ReDoc endpoint
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "defaultOperationsExpandDepth": 0,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "filter": False,
        # "deepLinking": True
    }
)

# Register the middleware


app.mount("/static", StaticFiles(directory="app/data"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Adding CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use caution in production)
    allow_credentials=True,  
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Settings for JWT
class Settings(BaseModel):
    authjwt_secret_key: str = Config.JWT_SECRET_KEY
    authjwt_access_token_expires: int = Config.ACCESS_TOKEN_EXPIREY  # Access token expires in 60 seconds
    authjwt_refresh_token_expires: int = Config.REFRESH_TOKEN_EXPIREY  # Refresh token expires in 1 hour

@AuthJWT.load_config
def get_config():
    return Settings()

# Add middleware
app.add_middleware(CheckRevokedTokenMiddleware, get_db=get_db)

@app.get("/api-docs.html", include_in_schema=False)
async def get_swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate_swagger_ui)):
    from fastapi.openapi.docs import get_swagger_ui_html
    """Serve Swagger UI with Basic Auth and Custom Tab Title."""
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=swagger_config["title"],  # Custom title directly here
        swagger_favicon_url="/static/favicon.ico",  # Optional: Add a favicon
        swagger_ui_parameters=app.swagger_ui_parameters  # Apply the custom settings
    )
    return HTMLResponse(content=html_response.body)

@app.get("/redoc.html", include_in_schema=False)
async def get_redoc_ui(credentials: HTTPBasicCredentials = Depends(authenticate_swagger_ui)):
    """Serve ReDoc UI with Basic Auth and Custom Tab Title"""
    from fastapi.openapi.docs import get_redoc_html
    html_response = get_redoc_html(openapi_url=app.openapi_url, title=app.title)
    # Modify the HTML content to replace the default title
    html_content = html_response.body.decode()  # Decode the content to string
    # Return the modified HTML content as an HTMLResponse
    return HTMLResponse(content=html_content)

# Exception Handlers
@app.exception_handler(AuthJWTException)
def custom_authjwt_exception_handler(request, exc):
    return authjwt_exception_handler(request, exc)



# register admin
app.include_router(admin_auth_router.router, prefix=Config.API_VERSION_ADMIN)
app.include_router(role_permission_router.router, prefix=Config.API_VERSION_ADMIN)
app.include_router(existing_api_router.router, prefix=Config.API_VERSION_ADMIN)
# register front



@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        loc = error["loc"]
        msg = error["msg"]

        # Identify the field causing the error
        if loc[0] == "body" and len(loc) > 1:
            if loc[1] == "user":
                field = loc[-1]  # Field in the UserRegister model
            elif loc[1] == "images":
                field = "images"
            else:
                field = loc[1]
        else:
            field = "general"

        # Group errors by field
        if field not in errors:
            errors[field] = []
        errors[field].append(msg)

    return JSONResponse(
        status_code=400,
        content=errors,
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=swagger_config["title"],
        version=swagger_config["version"],
        description=swagger_config["description"],
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload



