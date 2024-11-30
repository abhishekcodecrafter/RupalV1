from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, OTP, UserStatus
from .utils import generate_otp, generate_referral_code, send_sms_otp

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        if not mobile:
            flash('Mobile number is required', 'error')
            return redirect(url_for('auth.login'))

        # Generate and send OTP
        otp = generate_otp()
        new_otp = OTP(mobile=mobile, otp=otp, purpose='LOGIN')
        db.session.add(new_otp)
        db.session.commit()

        send_sms_otp(mobile, otp)
        session['temp_mobile'] = mobile

        return redirect(url_for('auth.verify_otp'))

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        referral_code = request.form.get('referral_code')

        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile number already registered', 'error')
            return redirect(url_for('auth.signup'))

        # Generate and send OTP
        otp = generate_otp()
        new_otp = OTP(mobile=mobile, otp=otp, purpose='SIGNUP')
        db.session.add(new_otp)
        db.session.commit()

        send_sms_otp(mobile, otp)
        session['temp_mobile'] = mobile
        session['temp_referral'] = referral_code

        return redirect(url_for('auth.verify_signup_otp'))

    return render_template('signup.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_mobile' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        mobile = session['temp_mobile']

        otp_record = OTP.query.filter_by(
            mobile=mobile,
            otp=otp,
            purpose='LOGIN',
            is_verified=False
        ).first()

        if not otp_record:
            flash('Invalid OTP', 'error')
            return redirect(url_for('auth.verify_otp'))

        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))

        session.pop('temp_mobile', None)
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin

        return redirect(url_for('dashboard.index'))

    return render_template('verify_otp.html')


@auth_bp.route('/verify-signup-otp', methods=['GET', 'POST'])
def verify_signup_otp():
    if 'temp_mobile' not in session:
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        wallet_pin = request.form.get('wallet_pin')
        mobile = session['temp_mobile']
        referral_code = session.get('temp_referral')

        if not all([otp, wallet_pin]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.verify_signup_otp'))

        otp_record = OTP.query.filter_by(
            mobile=mobile,
            otp=otp,
            purpose='SIGNUP',
            is_verified=False
        ).first()

        if not otp_record:
            flash('Invalid OTP', 'error')
            return redirect(url_for('auth.verify_signup_otp'))

        new_user = User(
            mobile=mobile,
            status=UserStatus.ACTIVE,
            referral_code=generate_referral_code()
        )
        new_user.set_wallet_pin(wallet_pin)

        if referral_code:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                new_user.referred_by = referrer.id

        db.session.add(new_user)
        db.session.commit()

        session.pop('temp_mobile', None)
        session.pop('temp_referral', None)
        session['user_id'] = new_user.id

        return redirect(url_for('dashboard.index'))

    return render_template('verify_signup_otp.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))