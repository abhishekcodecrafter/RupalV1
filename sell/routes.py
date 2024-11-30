from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models import db, Transaction, TransactionType, TransactionStatus, User, BankAccount
from auth.utils import login_required
from decimal import Decimal

sell_bp = Blueprint('sell', __name__)


def get_current_rate(typee):
    return 89.50


@sell_bp.route('/', methods=['GET'])
@login_required
def index():
    """Sell USDT landing page"""
    bank_accounts = BankAccount.query.filter_by(user_id=session['user_id']).all()
    rate = get_current_rate("")
    user = User.query.filter_by(id=session['user_id']).with_for_update().first()
    return render_template('sell/index.html',
                           bank_accounts=bank_accounts,
                           rate=rate,
                           current_user = user
                           )


@sell_bp.route('/initiate', methods=['POST'])
@login_required
def initiate():
    amount_usdt = float(request.form.get('amount_usdt', 0))
    bank_account_id = request.form.get('bank_account_id')

    if amount_usdt < current_app.config['MIN_SELL_USDT']:
        flash(f'Minimum sell amount is {current_app.config["MIN_SELL_USDT"]} USDT', 'error')
        return redirect(url_for('sell.index'))

    bank_account = BankAccount.query.filter_by(
        id=bank_account_id,
        user_id=session['user_id']
    ).first()

    if not bank_account:
        flash('Invalid bank account', 'error')
        return redirect(url_for('sell.index'))

    # Check balance
    user = User.query.filter_by(id=session['user_id']).with_for_update().first()
    if user.wallet_balance < amount_usdt:
        flash('Insufficient balance', 'error')
        return redirect(url_for('sell.index'))

    try:
        rate = get_current_rate("gg")
        amount_inr = amount_usdt * rate

        transaction = Transaction(
            user_id=session['user_id'],
            transaction_type=TransactionType.SELL,
            amount_usdt=amount_usdt,
            amount_inr=amount_inr,
            exchange_rate=rate,
            bank_account_id=bank_account.id,
            status=TransactionStatus.PROCESSING
        )

        # Deduct from wallet
        user.wallet_balance -= amount_usdt

        db.session.add(transaction)
        db.session.commit()

        flash('Sell order placed successfully', 'success')
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Error processing sell order', 'error')
        return redirect(url_for('sell.index'))
