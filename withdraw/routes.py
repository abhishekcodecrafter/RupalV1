from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Transaction, TransactionType, TransactionStatus, User, WithdrawalAddress
from auth.utils import login_required
from .utils import validate_tron_address

withdraw_bp = Blueprint('withdraw', __name__)


@withdraw_bp.route('/', methods=['GET'])
@login_required
def index():
    """Withdrawal landing page"""
    addresses = WithdrawalAddress.query.filter_by(user_id=session['user_id']).all()
    user = User.query.get(session['user_id'])
    return render_template('withdraw/index.html',
                           addresses=addresses,
                           balance=user.wallet_balance,
                           fee=current_app.config['BASE_WITHDRAWAL_FEE']
                           )


@withdraw_bp.route('/address/add', methods=['POST'])
@login_required
def add_address():
    address = request.form.get('address')
    label = request.form.get('label', '')

    if not validate_tron_address(address):
        flash('Invalid TRON address', 'error')
        return redirect(url_for('withdraw.index'))

    try:
        withdrawal_address = WithdrawalAddress(
            user_id=session['user_id'],
            address=address,
            label=label
        )
        db.session.add(withdrawal_address)
        db.session.commit()

        flash('Address added successfully', 'success')
    except:
        flash('Error adding address', 'error')

    return redirect(url_for('withdraw.index'))


@withdraw_bp.route('/initiate', methods=['POST'])
@login_required
def initiate():
    amount = float(request.form.get('amount', 0))
    address = request.form.get('address')
    wallet_pin = request.form.get('wallet_pin')

    if amount < current_app.config['MIN_WITHDRAWAL_USDT']:
        flash(f'Minimum withdrawal amount is {current_app.config["MIN_WITHDRAWAL_USDT"]} USDT', 'error')
        return redirect(url_for('withdraw.index'))

    fee = current_app.config['BASE_WITHDRAWAL_FEE']
    total_amount = amount + fee

    user = User.query.filter_by(id=session['user_id']).with_for_update().first()

    if not user.check_wallet_pin(wallet_pin):
        flash('Invalid wallet PIN', 'error')
        return redirect(url_for('withdraw.index'))

    if user.wallet_balance < total_amount:
        flash('Insufficient balance', 'error')
        return redirect(url_for('withdraw.index'))

    try:
        # Create withdrawal transaction
        transaction = Transaction(
            user_id=session['user_id'],
            transaction_type=TransactionType.WITHDRAW,
            amount_usdt=amount,
            fee_usdt=fee,
            to_address=address,
            status=TransactionStatus.PENDING
        )

        # Deduct from wallet
        user.wallet_balance -= total_amount

        db.session.add(transaction)
        db.session.commit()

        flash('Withdrawal request submitted successfully', 'success')
        return redirect(url_for('dashboard.index'))

    except:
        db.session.rollback()
        flash('Error processing withdrawal', 'error')
        return redirect(url_for('withdraw.index'))