import os
from datetime import timedelta


class Config:
    # Basic Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///crypto_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Config
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload Config
    UPLOAD_DIR = 'uploads/payment_proofs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Transaction Limits
    MIN_BUY_INR = 1000
    MAX_BUY_INR = 1000000
    MIN_SELL_USDT = 10
    MAX_SELL_USDT = 10000
    MIN_WITHDRAWAL_USDT = 10
    MAX_WITHDRAWAL_USDT = 10000
    BASE_WITHDRAWAL_FEE = 1

    # Bank Details
    BANK_ACCOUNT_NAME = 'Company Name'
    BANK_ACCOUNT_NUMBER = '1234567890'
    BANK_IFSC_CODE = 'ABCD0123456'
    BANK_NAME = 'Bank Name'
    BANK_BRANCH = 'Main Branch'

    # Platform Wallet
    PLATFORM_WALLET_ADDRESS = "THdwjNJM1uYMMCBYWyVPnqX5VffoJARYAh"

    # TRON Network
    TRON_API_URL = 'https://api.trongrid.io'
    MIN_CONFIRMATIONS = 1

    # Referral System
    MAX_REFERRAL_LEVELS = 5

    # OTP Settings
    OTP_LENGTH = 6
    OTP_VALIDITY_MINUTES = 10

    BANK_DETAILS = {}