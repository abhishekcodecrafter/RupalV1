import random
import string
from functools import wraps
from flask import session, redirect, url_for, flash
import re

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_referral_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

def send_sms_otp(mobile, otp):
    # Implement your SMS gateway integration here
    print(f"Sending OTP {otp} to {mobile}")
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'error')
            return redirect(url_for('auth.login'))
        if not session.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function