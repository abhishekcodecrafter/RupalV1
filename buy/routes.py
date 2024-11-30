# buy/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from models import db, Transaction, TransactionType, TransactionStatus, User
from auth.utils import login_required, admin_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from sell.routes import get_current_rate

buy_bp = Blueprint('buy', __name__)


@buy_bp.route('/', methods=['GET'])
@login_required
def index():
    """Buy USDT landing page"""
    rate = get_current_rate("buy")
    return render_template('buy/index.html', rate=rate)


@buy_bp.route('/initiate', methods=['GET', 'POST'])
@login_required
def initiate():
    if request.method == 'POST':
        amount_inr = float(request.form.get('amount_inr', 0))
        if amount_inr < current_app.config['MIN_BUY_INR']:
            flash(f'Minimum buy amount is {current_app.config["MIN_BUY_INR"]} INR', 'error')
            return redirect(url_for('buy.initiate'))

        rate = get_current_rate("buy")
        amount_usdt = amount_inr / float(rate)

        transaction = Transaction(
            user_id=session['user_id'],
            transaction_type=TransactionType.BUY,
            amount_usdt=amount_usdt,
            amount_inr=amount_inr,
            exchange_rate=rate,
            status=TransactionStatus.PENDING
        )

        db.session.add(transaction)
        db.session.commit()

        return render_template('buy/confirm.html',
                               transaction=transaction,
                               bank_details=current_app.config['BANK_DETAILS']
                               )

    return render_template('buy/initiate.html')


@buy_bp.route('/confirm/<int:transaction_id>', methods=['POST'])
@login_required
def confirm(transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=session['user_id'],
        status=TransactionStatus.PENDING
    ).first_or_404()

    if 'payment_proof' not in request.files:
        flash('Payment proof is required', 'error')
        return redirect(url_for('buy.confirm', transaction_id=transaction_id))

    payment_proof = request.files['payment_proof']
    reference_number = request.form.get('reference_number')

    if not reference_number:
        flash('Reference number is required', 'error')
        return redirect(url_for('buy.confirm', transaction_id=transaction_id))

    if payment_proof:
        filename = secure_filename(
            f"{transaction_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{payment_proof.filename}")
        payment_proof.save(os.path.join(current_app.config['UPLOAD_DIR'], filename))

        transaction.payment_proof = filename
        transaction.payment_reference = reference_number
        transaction.status = TransactionStatus.PROCESSING

        db.session.commit()

        flash('Payment proof submitted successfully', 'success')
        return redirect(url_for('dashboard.index'))

    flash('Error uploading payment proof', 'error')
    return redirect(url_for('buy.confirm', transaction_id=transaction_id))