from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import (
    db, User, Transaction, BankAccount, ReferralCommission,
    TransactionStatus, TransactionType, UserStatus
)
from auth.utils import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(status=UserStatus.ACTIVE).count(),
        'pending_transactions': Transaction.query.filter_by(status=TransactionStatus.PENDING).count(),
        'total_volume': db.session.query(db.func.sum(Transaction.amount_usdt)).filter_by(
            status=TransactionStatus.COMPLETED
        ).scalar() or 0
    }

    # Recent transactions
    recent_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).limit(10).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_transactions=recent_transactions
                           )


@admin_bp.route('/transactions')
@admin_required
def transactions():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    tx_type = request.args.get('type')

    query = Transaction.query

    if status:
        query = query.filter_by(status=TransactionStatus(status))
    if tx_type:
        query = query.filter_by(transaction_type=TransactionType(tx_type))

    transactions = query.order_by(
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=20)

    return render_template('admin/transactions.html',
                           transactions=transactions,
                           statuses=TransactionStatus,
                           types=TransactionType
                           )


@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)

    if user.status == UserStatus.ACTIVE:
        user.status = UserStatus.SUSPENDED
    else:
        user.status = UserStatus.ACTIVE

    db.session.commit()
    flash(f'User status updated to {user.status.value}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/bank-accounts')
@admin_required
def bank_accounts():
    page = request.args.get('page', 1, type=int)
    accounts = BankAccount.query.order_by(
        BankAccount.created_at.desc()
    ).paginate(page=page, per_page=20)
    return render_template('admin/bank_accounts.html', accounts=accounts)


@admin_bp.route('/referral/commission', methods=['GET', 'POST'])
@admin_required
def referral_commission():
    if request.method == 'POST':
        level = request.form.get('level', type=int)
        buy_commission = request.form.get('buy_commission', type=float)
        sell_commission = request.form.get('sell_commission', type=float)

        commission = ReferralCommission.query.filter_by(level=level).first()
        if not commission:
            commission = ReferralCommission(level=level)

        commission.buy_commission_percent = buy_commission
        commission.sell_commission_percent = sell_commission

        db.session.add(commission)
        db.session.commit()

        flash('Commission rates updated successfully', 'success')
        return redirect(url_for('admin.referral_commission'))

    commission_rates = ReferralCommission.query.order_by(ReferralCommission.level).all()
    return render_template('admin/referral_commission.html', commission_rates=commission_rates)
