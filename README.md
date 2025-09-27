# DeelflowAI Backend (FastAPI)

## Overview

DeelflowAI Backend is a FastAPI-based RESTful API server for real estate business metrics, campaign management, user authentication, and analytics. It uses PostgreSQL for data storage and SQLAlchemy ORM for database interaction. JWT authentication and role-based permissions are supported.

---

## Features

- **User Authentication**: JWT-based login, registration, and profile management.
- **Role & Permission Management**: Assign roles and granular menu permissions to users.
- **Business Metrics**: Track revenue, active users, properties listed, deals, profit, and AI conversations.
- **Campaign Management**: Create, update, and analyze campaigns, leads, and property stats.
- **Compliance & Audit**: Monitor compliance status, audit trails, and system health.
- **Historical & Analytical Data**: Access historical metrics, conversion funnels, and performance charts.
- **Swagger & ReDoc Documentation**: Secured API docs with Basic Auth.
- **File Uploads**: Support for file and image uploads.
- **Extensible Models**: Modular models for users, campaigns, leads, devices, permissions, etc.

---

## Project Structure

```
.
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── db_connection.py
│   │   ├── main_config.py
│   │   └── swagger_config.py
│   ├── models/
│   │   ├── activityfeed.py
│   │   ├── businessmetrics.py
│   │   ├── campaign.py
│   │   ├── campaignperformance.py
│   │   ├── campaignpropertystats.py
│   │   ├── channel.py
│   │   ├── channelresponserate.py
│   │   ├── compliancestatus.py
│   │   ├── devices.py
│   │   ├── historicalmetrics.py
│   │   ├── jwt_tokens.py
│   │   ├── lead.py
│   │   ├── menus.py
│   │   ├── organization.py
│   │   ├── roles.py
│   │   ├── user.py
│   │   └── user_menu_permissions.py
│   ├── routers/
│   │   ├── admin/
│   │   │   ├── auth_router.py
│   │   │   ├── existing_api_router.py
│   │   │   └── role_permission_router.py
│   ├── schemas/
│   │   └── admin/
│   │       └── auth.py
│   ├── utils/
│   │   ├── exceptions.py
│   │   ├── helpers.py
│   │   └── middlewares.py
│   └── data/
├── db/
│   └── deelflow_backup.sql
├── uploads/
│   ├── docs/
│   └── images/
├── requirements.txt
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/agarwalpacker12/deelflowai-backend-fastapi.git
cd deelflowai-backend-fastapi
```

### 2. Install Dependencies

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `app/config/main_config.py` for database credentials, JWT secret, and other settings.

### 4. Database Setup

- Ensure PostgreSQL is running.
- Create a database named `deelflow_db`.
- Restore schema and sample data:

```sh
psql -U postgres -d deelflow_db -f db/deelflow_backup.sql
```

### 5. Run the Server

```sh
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## API Documentation

- **Swagger UI**: [http://localhost:8001/api-docs.html](http://localhost:8001/api-docs.html)
- **ReDoc**: [http://localhost:8001/redoc.html](http://localhost:8001/redoc.html)

> Both docs require Basic Auth (`api` / `passw0rd` by default).

---

## Key Endpoints

### Authentication

- `POST /api/v1/admin/login` — Admin login
- `POST /api/v1/admin/create-user` — Register new user

### Metrics & Analytics

- `GET /api/v1/admin/total-revenue`
- `GET /api/v1/admin/active-users`
- `GET /api/v1/admin/properties-listed`
- `GET /api/v1/admin/ai-conversations`
- `GET /api/v1/admin/monthly-profit`
- `GET /api/v1/admin/compliance-status`
- `GET /api/v1/admin/historical-performance`

### Campaigns & Leads

- `GET /api/v1/admin/active_campaign_summary`
- `GET /api/v1/admin/lead_conversion_funnel`
- `GET /api/v1/admin/campaign_performance_overview`
- `GET /api/v1/admin/campaign_property_stats`
- `GET /api/v1/admin/channel_response_rates`

### Property Analysis

- `POST /api/v1/admin/property_analysis`
- `POST /api/v1/admin/repair_analysis`
- `POST /api/v1/admin/recent_activity`
- `POST /api/v1/admin/neighborhood-analysis`
- `POST /api/v1/admin/market_comparables`

### Role & Permission Management

- `POST /api/v1/admin/assign-permissions`
- `GET /api/v1/admin/roles`
- `GET /api/v1/admin/permissions`

---

## Security

- JWT authentication for all protected endpoints.
- Role-based and menu-based permission checks.
- Revoked token middleware for session security.
- Basic Auth for API documentation.

---

## Development Notes

- Uses SQLAlchemy 2.x async ORM.
- Modular routers for admin and future front-end APIs.
- Custom OpenAPI schema and documentation.
- All models have `.to_dict()` for serialization.
- CORS enabled for all origins (change for production).

---

## License

This project is proprietary and not licensed for public use.

---

## Contact

For support or queries, contact the repository owner or open an issue.
