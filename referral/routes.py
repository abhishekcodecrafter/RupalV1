from flask import Blueprint, render_template, session, request, current_app
from models import db, User, ReferralEarning, ReferralCommission
from auth.utils import login_required, admin_required
from referral.utils import get_referral_tree

referral_bp = Blueprint('referral', __name__)


@referral_bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])

    # Get direct referrals
    direct_referrals = User.query.filter_by(referred_by=user.id).all()

    # Get earnings
    earnings = ReferralEarning.query.filter_by(
        user_id=session['user_id']
    ).order_by(ReferralEarning.created_at.desc()).limit(10).all()

    # Calculate total earnings
    total_earnings = sum(earning.amount_usdt for earning in
                         ReferralEarning.query.filter_by(user_id=session['user_id']).all())

    # Get commission rates
    commission_rates = ReferralCommission.query.filter_by(is_active=True).all()

    return render_template('referral/referrals.html',
                           user=user,
                           direct_referrals=direct_referrals,
                           earnings=earnings,
                           total_earnings=total_earnings,
                           commission_rates=commission_rates
                           )


@referral_bp.route('/earnings')
@login_required
def earnings():
    page = int(request.args.get('page', 1))
    earnings = ReferralEarning.query.filter_by(
        user_id=session['user_id']
    ).order_by(
        ReferralEarning.created_at.desc()
    ).paginate(page=page, per_page=20)

    return render_template('referral/earnings.html', earnings=earnings)


@referral_bp.route('/network')
@login_required
def network():
    user = User.query.get(session['user_id'])
    referrals = get_referral_tree(user.id)

    return render_template('referral/network.html',
                           referrals=referrals,
                           max_levels=current_app.config['MAX_REFERRAL_LEVELS']
                           )
