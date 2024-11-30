from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, BankAccount
from auth.utils import login_required, admin_required

bank_bp = Blueprint('bank', __name__)


@bank_bp.route('/accounts', methods=['GET'])
@login_required
def list_accounts():
    accounts = BankAccount.query.filter_by(user_id=session['user_id']).all()
    return render_template('bank/accounts.html', accounts=accounts)


@bank_bp.route('/accounts/add', methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        account_number = request.form.get('account_number')
        ifsc_code = request.form.get('ifsc_code')
        account_holder = request.form.get('account_holder')
        bank_name = request.form.get('bank_name')

        # Basic validation
        if not all([account_number, ifsc_code, account_holder, bank_name]):
            flash('All fields are required', 'error')
            return redirect(url_for('bank.add_account'))

        # IFSC code validation
        if not ifsc_code.isalnum() or len(ifsc_code) != 11:
            flash('Invalid IFSC code', 'error')
            return redirect(url_for('bank.add_account'))

        try:
            bank_account = BankAccount(
                user_id=session['user_id'],
                account_number=account_number,
                ifsc_code=ifsc_code.upper(),
                account_holder=account_holder,
                bank_name=bank_name
            )

            db.session.add(bank_account)
            db.session.commit()

            flash('Bank account added successfully', 'success')
            return redirect(url_for('bank.list_accounts'))

        except Exception as e:
            db.session.rollback()
            flash('Error adding bank account', 'error')
            return redirect(url_for('bank.add_account'))

    return render_template('bank/add_account.html')


@bank_bp.route('/accounts/<int:account_id>/delete', methods=['POST'])
@login_required
def delete_account(account_id):
    account = BankAccount.query.filter_by(
        id=account_id,
        user_id=session['user_id']
    ).first_or_404()

    try:
        db.session.delete(account)
        db.session.commit()
        flash('Bank account deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('Error deleting bank account', 'error')

    return redirect(url_for('bank.list_accounts'))


# Bank account verification route (for admin)
@bank_bp.route('/admin/accounts/verify/<int:account_id>', methods=['POST'])
@admin_required
def verify_account(account_id):
    account = BankAccount.query.get_or_404(account_id)

    try:
        account.is_verified = True
        db.session.commit()
        flash('Bank account verified successfully', 'success')
    except:
        db.session.rollback()
        flash('Error verifying bank account', 'error')

    return redirect(url_for('admin.bank_accounts'))