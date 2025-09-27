from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from typing import Dict, Optional, List, Union
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from user_agents import parse
from sqlalchemy import update
from passlib.hash import django_pbkdf2_sha256

from app.config.db_connection import get_db
import app.utils.helpers as helpers
from app.config.main_config import Config
from app.utils.helpers import jwt_required_admin

from app.schemas.admin.auth import *
from app.models.user import User
from app.models.menus import Menus
from app.models.user_menu_permissions import UserMenuPermissions


router = APIRouter(tags=["Admin - Role Menu Permission"])


class MenuPermissionPayload(BaseModel):
    menu_id: int
    can_add: Union[bool, int] = 1
    can_edit: Union[bool, int] = 0
    can_delete: Union[bool, int] = 0
    can_view: Union[bool, int] = 0
    can_download: Union[bool, int] = 0

class AssignPermissionsRequest(BaseModel):
    user_id: int
    permissions: List[MenuPermissionPayload]



@router.get("/list-user")
@jwt_required_admin()
async def list_users(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
        )
        users = result.scalars().all()

        return {
            "message": "Users fetched successfully.",
            "data": [user.to_dict() for user in users],
        }

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        print(str(db_ex))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")


@router.get("/list-menus")
@jwt_required_admin()
async def list_menus(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Menus)
            .where(Menus.is_active == True)
        )
        menus = result.scalars().all()

        return {
            "message": "Menus fetched successfully.",
            "data": [menu.to_dict() for menu in menus],
        }

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        print(str(db_ex))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    

@router.post("/assign-permission")
@jwt_required_admin()
async def assign_permission(request: Request, payload: AssignPermissionsRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .where(User.is_active == True, User.id == payload.user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")

        menu_ids = [p.menu_id for p in payload.permissions]
        result = await db.execute(select(Menus).where(Menus.id.in_(menu_ids)))
        existing_menus = {m.id for m in result.scalars().all()}

        for perm in payload.permissions:
            if perm.menu_id not in existing_menus:
                raise HTTPException(status_code=404, detail=f"Menu {perm.menu_id} not found")
            
            # Check if record already exists
            result = await db.execute(
                select(UserMenuPermissions).where(
                    UserMenuPermissions.user_id == payload.user_id,
                    UserMenuPermissions.menu_id == perm.menu_id,
                )
            )
            record = result.scalar_one_or_none()

            if record:
                # Update existing
                record.can_add = perm.can_add
                record.can_edit = perm.can_edit
                record.can_delete = perm.can_delete
                record.can_view = perm.can_view
                record.can_download = perm.can_download
            else:
                # Create new
                new_perm = UserMenuPermissions(
                    user_id=payload.user_id,
                    menu_id=perm.menu_id,
                    can_add=perm.can_add,
                    can_edit=perm.can_edit,
                    can_delete=perm.can_delete,
                    can_view=perm.can_view,
                    can_download=perm.can_download,
                )
                db.add(new_perm)

        await db.commit()

        result = await db.execute(
            select(User)
            .options(
                selectinload(User.menu_permissions)  # Load UserMenuPermissions
                    .selectinload(UserMenuPermissions.menu)  # Load related Menus
            )
            .where(User.is_active == True, User.id == payload.user_id)
        )
        user = result.scalars().first()

        return {
            "message": "Permissions updated successfully.",
            "data": user.to_dict_menu(),
        }

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        print(str(db_ex))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    

@router.get("/list-user-role-menus")
@jwt_required_admin()
async def list_user_role_menus(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.organization),
                selectinload(User.menu_permissions)
                    .selectinload(UserMenuPermissions.menu)
            )
            .where(User.is_active == True)
        )
        users = result.scalars().all()

        return {
            "message": "Users fetched successfully.",
            "data": [user.to_dict_menu() for user in users],
        }

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        print(str(db_ex))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    

@router.get("/user-role-menus-by-id/{user_id}")
@jwt_required_admin()
async def user_role_menus_by_id(request: Request,user_id: int,  Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.organization),
                selectinload(User.menu_permissions)
                    .selectinload(UserMenuPermissions.menu)
            )
            .where(User.is_active == True, User.id == user_id)
        )
        user = result.scalars().first()

        return {
            "message": "Users fetched successfully.",
            "data": user.to_dict_menu()
        }

    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        print(str(db_ex))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    



