from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session

from deposit import deposit_bp
from models import (
    db, Transaction, TransactionType, TransactionStatus,
    PooledWallet, WalletAssignment, WalletStatus
)
from services.wallet_pool import WalletPoolService
from services.wallet_pool import BlockchainService
from auth.utils import login_required
import qrcode
import io
import base64

@deposit_bp.route('/')
@login_required
def index():
    """Landing page for deposit"""
    return render_template('deposit/index.html')


@deposit_bp.route('/initiate', methods=['POST'])
@login_required
def initiate_deposit():
    """Start deposit process"""
    data = request.get_json()
    if not data or 'amount_usdt' not in data:
        return jsonify({'error': 'Amount is required'}), 400

    try:
        amount = float(data['amount_usdt'])
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400

        # Get deposit address
        wallet_service = WalletPoolService()
        assignment = wallet_service.assign_wallet(session['user_id'], amount)

        if not assignment:
            return jsonify({'error': 'No deposit addresses available'}), 503

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(assignment.wallet.address)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            'deposit_address': assignment.wallet.address,
            'qr_code': qr_code,
            'amount_usdt': amount,
            'expires_at': assignment.expires_at.isoformat(),
            'assignment_id': assignment.id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@deposit_bp.route('/status/<int:assignment_id>', methods=['GET'])
@login_required
def check_status(assignment_id):
    """Check deposit status"""
    assignment = WalletAssignment.query.filter_by(
        id=assignment_id,
        user_id=session['user_id']
    ).first_or_404()

    # Get recent transactions for this address
    blockchain_service = BlockchainService()
    transactions = blockchain_service.get_wallet_transactions(
        assignment.wallet.address,
        start_time=assignment.assigned_at
    )

    completed_transactions = []
    total_received = 0

    for txn in transactions:
        if txn['to_address'].lower() == assignment.wallet.address.lower():
            amount = float(txn['value']) / 1e6
            total_received += amount
            completed_transactions.append({
                'hash': txn['hash'],
                'amount': amount,
                'confirmations': txn['confirmations'],
                'timestamp': datetime.fromtimestamp(txn['timestamp'] / 1000).isoformat()
            })

    return jsonify({
        'status': 'EXPIRED' if datetime.utcnow() > assignment.expires_at else 'ACTIVE',
        'address': assignment.wallet.address,
        'expected_amount': assignment.expected_amount,
        'total_received': total_received,
        'transactions': completed_transactions,
        'expires_at': assignment.expires_at.isoformat()
    })