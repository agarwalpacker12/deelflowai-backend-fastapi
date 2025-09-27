from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from typing import Dict, Optional, List
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
from app.models.devices import Device
from app.models.jwt_tokens import JwtToken
from app.models.organization import Organization

s = URLSafeTimedSerializer(Config.JWT_SECRET_KEY)

router = APIRouter(tags=["Admin - Authentication"])



@router.post("/login")
async def login_admin(request: Request, data: AdminLogin, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        result = await db.execute(
            select(User)
            .where(User.email == data.email)
        )
        user = result.scalars().first()

        if not user or not django_pbkdf2_sha256.verify(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Check user role
        # if user.role_id not in [1, 2]:
        #     raise HTTPException(status_code=403, detail="Unauthorized user type for login")

        # Check if the user is inactive
        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Your account has been deactivated by the admin. Please contact support for further assistance.",
            )
        
        # Get IP and User-Agent info
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent')

        parsed_ua = parse(user_agent) if user_agent else None
        # Basic details
        browser_name = parsed_ua.browser.family if parsed_ua else "Unknown"
        os_name = parsed_ua.os.family if parsed_ua else "Unknown"
        # Save device information
        add_device = Device(
            user_id=user.id,
            device_ip=client_ip,
            device_os=os_name,
            device_name=browser_name,
        )
        db.add(add_device)
        await db.commit()
        await db.refresh(add_device)

        # Create access and refresh tokens
        access_jti = helpers.generate_jti()
        refresh_jti = helpers.generate_jti()

        additional_claims_access = {
            'jti': access_jti, 
            'device_id': add_device.id, 
            'user_type': user.role
        }
        additional_claims_refresh = {
            'jti': refresh_jti, 
            'device_id': add_device.id, 
            'user_type': user.role
        }

        access_token = Authorize.create_access_token(
            subject=user.id, 
            user_claims=additional_claims_access
        )
        refresh_token = Authorize.create_refresh_token(
            subject=user.id, 
            user_claims=additional_claims_refresh
        )

        # Save JWT tokens in the database
        add_jwt_token = JwtToken(
            user_id=user.id,
            device_id=add_device.id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            # device_ip=client_ip,
        )
        db.add(add_jwt_token)
        await db.commit()
        await db.refresh(add_jwt_token)

        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            "user": user.to_dict()
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
    

@router.post("/create-user")
async def create_user(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        # Check existing email
        existing_user = await db.execute(select(User).where(User.email == data.email))
        if existing_user.scalars().first():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Check existing organization slug
        existing_slug = await db.execute(select(Organization).where(Organization.slug == data.organization.slug))
        if existing_slug.scalars().first():
            raise HTTPException(status_code=400, detail="Organization slug already exists")
        
        # Create organization
        new_org = Organization(
            uuid=data.uuid,
            name=data.organization.name,
            slug=data.organization.slug,
            subscription_status=data.organization.subscription_status
        )
        db.add(new_org)
        await db.flush()  # Ensure new_org.id is available
        
        # Create user with hashed password
        new_user = User(
            uuid=data.uuid,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=data.role,
            level=data.level,
            points=data.points,
            is_verified=data.is_verified,
            is_active=data.is_active,
            stripe_customer_id=data.stripe_customer_id,
            password=django_pbkdf2_sha256.hash(data.password),
            organization_id=new_org.id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        await db.refresh(new_org)

        return {
            "message": "Registered Successfully.",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "organization": {
                    "id": new_org.id,
                    "name": new_org.name,
                    "slug": new_org.slug,
                    "subscription_status": new_org.subscription_status
                }
            }
        }
    
    except HTTPException as http_ex:
        raise http_ex
    except SQLAlchemyError as db_ex:
        await db.rollback()
        print(str(db_ex))
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        await db.rollback()
        print(str(e))
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")


@router.get("/me")
@jwt_required_admin()
async def admin_profile_data(
    request: Request,
    db: AsyncSession = Depends(get_db), 
    Authorize: AuthJWT = Depends()
):
    try:
        current_user = Authorize.get_jwt_subject()
        # Fetch user asynchronously
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == current_user)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            'message': 'User found',
            "data": user.to_dict()
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


@router.post("/refresh-token")
@jwt_required_admin(refresh=True)
async def admin_token_refresh(request: Request, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:

        current_user = Authorize.get_jwt_subject()
        device_id = Authorize.get_raw_jwt()['device_id']
        user_type = Authorize.get_raw_jwt()['user_type']
        jti = Authorize.get_raw_jwt()['jti']

        # Get IP and User-Agent info
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent')
        # Generate new access token and additional claims
        access_jti = helpers.generate_jti()

        additional_claims = {
            'jti': access_jti,
            'device_id': device_id,
            'user_type': user_type
        }

        # Query the JWT token from the database asynchronously
        result = await db.execute(
            select(JwtToken)
            .where(JwtToken.user_id == current_user, 
                   JwtToken.device_id == device_id, 
                   JwtToken.refresh_jti == jti, 
                   JwtToken.revoked == False)
        )
        update_jwt_token = result.scalars().first()

        if update_jwt_token:
            # Create new access token
            new_access_token = Authorize.create_access_token(
                subject=current_user, 
                user_claims=additional_claims
            )

            # Update the JWT token record
            update_jwt_token.access_jti = access_jti
            await db.commit()  # Commit the updated token record

            # Update the device table with the latest login time
            device_result = await db.execute(
                select(Device).where(Device.user_id == current_user, Device.id == device_id)
            )
            update_device = device_result.scalars().first()

            result = await db.execute(
                select(User)
                .where(User.id == current_user)
            )
            user = result.scalars().first()

            return {
                'message': 'New access token generated successfully',
                "access_token": new_access_token
            }
        else:
            raise HTTPException(status_code=401, detail="User already logged out! Please log in again.")
    
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


@router.delete("/logout")
@jwt_required_admin()
async def admin_logout(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        current_user = Authorize.get_jwt_subject()
        jti = Authorize.get_raw_jwt()['jti']
        device_id = Authorize.get_raw_jwt()['device_id']

        # Fetch the JWT token entry
        result = await db.execute(
            select(JwtToken).filter_by(user_id=current_user, device_id=device_id, access_jti=jti, revoked=False)
        )
        jwt_token = result.scalars().first()

        if jwt_token:
            jwt_token.revoked = True
            await db.commit()  # Commit changes asynchronously

            # Update the device table
            result = await db.execute(
                select(Device).filter_by(user_id=current_user, id=device_id)
            )
            update_device = result.scalars().first()

        return {'message': 'Successfully logged out'}
    
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


@router.delete("/logout-all-devices", status_code=status.HTTP_200_OK)
@jwt_required_admin()
async def admin_logout_all_devices(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        current_user_id = Authorize.get_jwt_subject()

        # Fetch all active tokens for the user
        result = await db.execute(select(JwtToken).filter_by(user_id=current_user_id, revoked=False))
        tokens = result.scalars().all()

        # Revoking all tokens
        for token in tokens:
            token.revoked = True

        await db.commit()  # Commit changes asynchronously

        return {"message": "Successfully logged out from all devices"}
    
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
