import os

class Config:
    
    
    FRONT_BASE_URL = ''
    ADMIN_BASE_URL = ''
    API_BASE_URL = 'http://127.0.0.1:8001'

    SECRET_KEY = 'defe#ap$00#'
    JWT_SECRET_KEY = '$$defe#ap$00#1#'
    TIME_ZONE = 'Asia/Kolkata'
    API_VERSION_USER = '/api/v1'
    API_VERSION_ADMIN = '/api/v1'
    SWAGGER_USER = "api"
    SWAGGER_PASS = "passw0rd"
    ACCESS_TOKEN_EXPIREY = 60 * 60 * 24
    REFRESH_TOKEN_EXPIREY = 60 * 60 * 24 * 365 * 3

    # for staging
    DB_HOST = 'localhost'
    DB_USER = 'postgres'
    DB_PASS = 'Awhpr148'
    DB_NAME = 'deelflow_db'
    DB_PORT = '5432'
    
    # for production
    # DB_HOST = ''
    # DB_USER = ''
    # DB_PASS = ''
    # DB_NAME = ''
    # DB_PORT = ''

    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = ''
    SMTP_PASSWORD = ''
    SMTP_SENDER_EMAIL = ''
    SMTP_REPLY_TO_EMAIL = ''
    SMTP_SENDER_NAME = ''




