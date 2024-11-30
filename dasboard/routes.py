from flask import Blueprint, render_template, session
from models import User, Transaction, BankAccount, WithdrawalAddress
from auth.utils import login_required
from sell.routes import get_current_rate

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    user = User.query.get(session['user_id'])

    # Get rates
    buy_rate = get_current_rate('buy')
    sell_rate = get_current_rate('sell')

    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(
        user_id=user.id
    ).order_by(
        Transaction.created_at.desc()
    ).limit(5).all()

    # Get bank accounts
    bank_accounts = BankAccount.query.filter_by(
        user_id=user.id
    ).all()

    # Get withdrawal addresses
    withdrawal_addresses = WithdrawalAddress.query.filter_by(
        user_id=user.id
    ).all()

    return render_template('dashboard/index.html',
                           current_user=user,
                           buy_rate=buy_rate,
                           sell_rate=sell_rate,
                           recent_transactions=recent_transactions,
                           bank_accounts=bank_accounts,
                           withdrawal_addresses=withdrawal_addresses
                           )


@dashboard_bp.route('/transactions')
@login_required
def transactions():
    # Implement transaction history page
    pass