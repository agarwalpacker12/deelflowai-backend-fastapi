from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from typing import Dict, Optional, List, Union
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import func, text, and_, or_, exists, desc

from app.config.db_connection import get_db
import app.utils.helpers as helpers
from app.config.main_config import Config
from app.utils.helpers import jwt_required_admin

from app.schemas.admin.auth import *
from app.models.user import User
from app.models.menus import Menus
from app.models.businessmetrics import BusinessMetrics
from app.models.compliancestatus import ComplianceStatus
from app.models.historicalmetrics import HistoricalMetrics
from app.models.activityfeed import ActivityFeed
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.channel import Channel
from app.models.campaignpropertystats import CampaignPropertyStats
from app.models.campaignperformance import CampaignPerformance
from app.models.channelresponserate import ChannelResponseRate

router = APIRouter(tags=["Admin - Existing API"])

class PropertyAnalysisRequest(BaseModel):
    address: str

class RepairAnalysisRequest(BaseModel):
    property_id: int
    address: str

class RecentActivityRequest(BaseModel):
    property_id: int
    address: str

class NeighborhoodAnalysisRequest(BaseModel):
    property_id: int
    address: str

class MarketComparablesRequest(BaseModel):
    property_id: int
    address: str


@router.post("/property_analysis")
@jwt_required_admin()
async def property_analysis(request: Request, data: PropertyAnalysisRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    address = data.address.strip()

    # ✅ Validation
    if not address:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Validation failed for property analysis",
                "error_code": "VALIDATION_ERROR",
                "errors": ["The address field is required."]
            }
        )

    # ⚡ Mock data (replace with DB calls or async calculations later)
    if address == "1247 Oak Street, Dallas, TX 75201":
        analysis_data = {
            "address": address,
            "lot_price": 85000,
            "estimated_arv": 158000,
            "repair_estimate": 23000,
            "cash_investor_max_offer": 38500,
            "market_info": {
                "open_markets": 4,
                "price_reductions": 2,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
        }
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Property data not found",
                "error_code": "PROPERTY_NOT_FOUND",
                "details": {"requested_address": address},
                "suggestions": [
                    "Verify the property address",
                    "Try searching with a property ID"
                ]
            }
        )

    # ✅ Success
    return {
        "status": "success",
        "message": "Property analysis generated successfully",
        "data": analysis_data
    }


@router.get("/total-revenue")
@jwt_required_admin()
async def total_revenue(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "total_revenue": None,
            }

        return {
            "message": "Data fetched successfully.",
            "total_revenue": latest_metrics.total_revenue,
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
    

@router.post("/repair_analysis")
@jwt_required_admin()
async def repair_analysis(request: Request, data: RepairAnalysisRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        repairs_data = {
            "HVAC": 4500,
            "Plumbing": 2200,
            "Electrical": 1700,
            "Roofing": 6500,
            "Flooring": 4000,
            "Kitchen": 5200
        }

        total_estimate = sum(repairs_data.values())
        return {
                "message": "Data fetched successfully.",
                "data": {
                    "property_id": data.property_id,
                    "address": data.address,
                    "repairs": repairs_data,
                    "total_estimate": total_estimate
                }
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
    

@router.post("/recent_activity")
@jwt_required_admin()
async def recent_activity(request: Request, data: RecentActivityRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        activities = [
            {"event": "Price reduced by $3,000", "date": "2025-06-10"},
            {"event": "New roof installed", "date": "2025-04-22"},
            {"event": "HVAC system serviced", "date": "2025-02-15"},
            {"event": "Listed for sale 18 months ago", "date": "2024-03-01"}
        ]

        return {
                "message": "Recent activity retrieved successfully.",
                "data": {
                    "property_id": data.property_id,
                    "address": data.address,
                    "activities": activities,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
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
    

@router.get("/active-users")
@jwt_required_admin()
async def active_users(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "active_users": None,
            }

        return {
            "message": "Data fetched successfully.",
            "active_users": latest_metrics.active_users,
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
    

@router.post("/neighborhood-analysis")
@jwt_required_admin()
async def neighborhood_analysis(request: Request, data: NeighborhoodAnalysisRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        neighborhood_data = {
            "appreciation": "3.2%",
            "crime_rate": "Low",
            "school_rating": "Medium"
        }

        return {
                "message": "Neighborhood analysis retrieved successfully.",
                "data": {
                    "property_id": data.property_id,
                    "address": data.address,
                    "neighborhood_metrics": neighborhood_data,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
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
    

@router.post("/market_comparables")
@jwt_required_admin()
async def market_comparables(request: Request, data: MarketComparablesRequest, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        comparables = {
            "similar_properties_count": 12,
            "examples": [
                {"address": "1250 Oak Street, Dallas, TX 75201", "price": 152000, "beds": 3, "baths": 2, "sqft": 1400},
                {"address": "1240 Pine Street, Dallas, TX 75201", "price": 160000, "beds": 4, "baths": 2, "sqft": 1550}
            ]
        }

        return {
                "message": "Neighborhood analysis retrieved successfully.",
                "data": {
                    "property_id": data.property_id,
                    "address": data.address,
                    "comparables": comparables,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
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
    


@router.get("/properties-listed")
@jwt_required_admin()
async def get_properties_listed(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "properties_listed": None,
            }

        return {
            "message": "Data fetched successfully.",
            "properties_listed": latest_metrics.properties_listed,
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
    
@router.get("/ai-conversations")
@jwt_required_admin()
async def get_ai_conversations(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "ai_conversations": None,
            }

        return {
            "message": "Data fetched successfully.",
            "ai_conversations": latest_metrics.ai_conversations,
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
    

@router.get("/total-deals")
@jwt_required_admin()
async def get_total_deals(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "total_deals": None,
            }

        return {
            "message": "Data fetched successfully.",
            "total_deals": latest_metrics.total_deals,
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
    

@router.get("/monthly-profit")
@jwt_required_admin()
async def get_monthly_profit(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "monthly_profit": None,
            }

        return {
            "message": "Data fetched successfully.",
            "monthly_profit": latest_metrics.monthly_profit,
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
    

@router.get("/voice-calls-count")
@jwt_required_admin()
async def get_voice_calls_count(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(BusinessMetrics)
            .order_by(desc(BusinessMetrics.report_date))
        )
        latest_metrics = result.scalars().first()
        if not latest_metrics:
            return {
                "message": "Data fetched successfully.",
                "voice_calls_count": None,
            }

        return {
            "message": "Data fetched successfully.",
            "voice_calls_count": latest_metrics.voice_calls_count,
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
    

@router.get("/compliance-status")
@jwt_required_admin()
async def get_compliance_status(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ComplianceStatus)
            .order_by(desc(ComplianceStatus.updated_at))
        )
        latest_status = result.scalars().first()
        if not latest_status:
            return {
                "message": "Data fetched successfully.",
                'compliance_percent': None,
                'audit_trail': None,
                'system_health': None,
                'updated_at': None
            }

        return {
            "message": "Data fetched successfully.",
            'compliance_percent': str(latest_status.compliance_percent),
			'audit_trail': latest_status.audit_trail,
			'system_health': latest_status.system_health,
			'updated_at': latest_status.updated_at
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
    

@router.get("/audit-trail-data")
@jwt_required_admin()
async def get_audit_trail_data(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ComplianceStatus)
            .order_by(desc(ComplianceStatus.updated_at))
        )
        latest_status = result.scalars().first()
        if not latest_status:
            return {
                "message": "Data fetched successfully.",
                'audit_trail': None
            }

        return {
            "message": "Data fetched successfully.",
			'audit_trail': latest_status.audit_trail
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
    

@router.get("/system-health-metrics")
@jwt_required_admin()
async def get_system_health_metrics(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ComplianceStatus)
            .order_by(desc(ComplianceStatus.updated_at))
        )
        latest_status = result.scalars().first()
        if not latest_status:
            return {
                "message": "Data fetched successfully.",
                'system_health': None
            }

        return {
            "message": "Data fetched successfully.",
			'system_health': latest_status.system_health
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
    

@router.get("/revenue-user-growth-chart-data")
@jwt_required_admin()
async def get_revenue_user_growth_chart_data(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(HistoricalMetrics)
            .where(HistoricalMetrics.metric_type == 'revenue')
            .order_by(desc(HistoricalMetrics.record_date))
        )
        revenue_data = result.scalars().all()

        result1 = await db.execute(
            select(HistoricalMetrics)
            .where(HistoricalMetrics.metric_type == 'active_users')
            .order_by(desc(HistoricalMetrics.record_date))
        )
        user_data = result1.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"revenue_chart": [rd.to_dict() for rd in revenue_data],
            "user_growth_chart": [ud.to_dict() for ud in user_data]
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
    

@router.get("/monthly-trend-data")
@jwt_required_admin()
async def get_monthly_trend_data(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(HistoricalMetrics)
            .where(HistoricalMetrics.metric_type == 'monthly_trend')
            .order_by(desc(HistoricalMetrics.record_date))
        )
        trend_data = result.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"monthly_trend_chart": [td.to_dict() for td in trend_data]
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
    

@router.get("/historical-performance")
@jwt_required_admin()
async def get_historical_performance(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(HistoricalMetrics)
            .order_by(desc(HistoricalMetrics.record_date))
        )
        performance_data = result.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"monthly_trend_chart": [pd.to_dict() for pd in performance_data]
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
    

@router.get("/live-activity-feed")
@jwt_required_admin()
async def get_live_activity_feed(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ActivityFeed)
            .order_by(desc(ActivityFeed.timestamp))
            .limit(50)
        )
        activities = result.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"live_activity_feed": [act.to_dict() for act in activities]
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
    

@router.get("/user-actions-timestamps")
@jwt_required_admin()
async def get_user_actions_timestamps(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ActivityFeed)
            .order_by(desc(ActivityFeed.timestamp))
            .limit(50)
        )
        activities = result.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"user_actions_timestamps": [act.to_dict() for act in activities]
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
    

@router.get("/deal-completions-scheduling")
@jwt_required_admin()
async def get_deal_completions_scheduling(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ActivityFeed)
            .filter(ActivityFeed.action_type == 'deal_completed')
            .order_by(desc(ActivityFeed.timestamp))
            .limit(50)
        )
        completions = result.scalars().all()

        result1 = await db.execute(
            select(ActivityFeed)
            .filter(ActivityFeed.action_type == 'deal_scheduled')
            .order_by(desc(ActivityFeed.timestamp))
            .limit(50)
        )
        scheduling = result1.scalars().all()
        return {
            "message": "Data fetched successfully.",
			"deal_completions": [co.to_dict() for co in completions],
            "deal_scheduling": [sc.to_dict() for sc in scheduling],
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
    

@router.get("/active_campaign_summary")
@jwt_required_admin()
async def active_campaign_summary(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        today = date.today()
        result = await db.execute(
            select(func.count(Campaign.id)).where(Campaign.status == "active")
        )
        total_active = result.scalar() 

        result = await db.execute(
            select(func.count(Lead.id)).where(func.date(Lead.created_at) == today)
        )
        leads_today = result.scalar()
        
        result_responded = await db.execute(
            select(func.count(Lead.id)).where(Lead.responded == True)
        )
        responded_count = result_responded.scalar() or 0

        # Total leads count
        result_total = await db.execute(
            select(func.count(Lead.id))
        )
        total_count = result_total.scalar() or 0

        # Calculate response rate
        response_rate = (responded_count / total_count * 100) if total_count else 0

        return {
            "message": "Data fetched successfully.",
			"data": {
                "total_active": total_active,
                "leads_today": leads_today,
                "leads_today_change_pct": 23,  # Optional: computed from history
                "response_rate": round(response_rate, 2)
            }
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
    

@router.get("/lead_conversion_funnel")
@jwt_required_admin()
async def lead_conversion_funnel(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(func.count(Lead.id)))
        leads_count = result.scalar() or 0

        result1 = await db.execute(
            select(func.count(Lead.id)).where(Lead.status == "qualified")
        )
        qualified_count = result1.scalar() or 0

        result2 = await db.execute(
            select(func.count(Lead.id)).where(Lead.status == "converted")
        )
        converted_count = result2.scalar() or 0

        return {
            "message": "Data fetched successfully.",
			"data": {
                "leads": leads_count,
                "qualified": qualified_count,
                "converted": converted_count
            }
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
    

@router.get("/channel_status")
@jwt_required_admin()
async def channel_status(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        channels = {}
        channel_names = ["email", "sms", "voice", "whatsapp"]

        for name in channel_names:
            result = await db.execute(
                select(exists().where(Channel.name == name, Channel.active == True))
            )
            is_active = result.scalar()
            
            if name == "whatsapp":
                channels[name] = "active" if is_active else "setup"
            else:
                channels[name] = "active" if is_active else "inactive"

        return {
            "message": "Data fetched successfully.",
			"data": channels
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
    

@router.get("/campaign_property_stats")
@jwt_required_admin()
async def campaign_property_stats(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(CampaignPropertyStats).order_by(desc(CampaignPropertyStats.updated_at))
        )
        stats = result.scalars().first()
        if not stats:
            raise HTTPException(status_code=404, detail="Data not found.")

        return {
            "message": "Data fetched successfully.",
			"data": stats.to_dict()
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
    

@router.get("/campaign_performance_overview")
@jwt_required_admin()
async def campaign_performance_overview(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CampaignPerformance))
        performances = result.scalars().all()
        if not performances:
            raise HTTPException(status_code=404, detail="Data not found.")

        return {
            "message": "Data fetched successfully.",
			"data": performances.to_dict()
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
    

@router.get("/channel_response_rates")
@jwt_required_admin()
async def channel_response_rates(request: Request, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ChannelResponseRate))
        channels = result.scalars().all()
        if not channels:
            raise HTTPException(status_code=404, detail="Data not found.")

        return {
            "message": "Data fetched successfully.",
			"data": channels.to_dict()
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