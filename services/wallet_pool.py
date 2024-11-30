from datetime import datetime, timedelta

import requests
from flask import current_app

from models import WalletAssignment, PooledWallet, WalletStatus, db, Transaction, TransactionType, TransactionStatus, \
    User


class WalletPoolService:
    def assign_wallet(self, user_id, amount, duration_minutes=30):
        """Assign a wallet to user for deposit"""
        # Check for existing active assignment
        existing = WalletAssignment.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(WalletAssignment.expires_at > datetime.utcnow()).first()

        if existing:
            return existing

        # Get available wallet
        wallet = (PooledWallet.query
                  .filter_by(status=WalletStatus.AVAILABLE)
                  .order_by(
            PooledWallet.last_used_at.asc(),
            PooledWallet.total_assignments.asc()
        )
                  .with_for_update()
                  .first())

        if not wallet:
            return None

        try:
            # Create assignment
            assignment = WalletAssignment(
                wallet_id=wallet.id,
                user_id=user_id,
                expected_amount=amount,
                expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes)
            )

            # Update wallet status
            wallet.status = WalletStatus.IN_USE
            wallet.last_used_at = datetime.utcnow()
            wallet.total_assignments += 1

            db.session.add(assignment)
            db.session.commit()

            return assignment

        except Exception as e:
            db.session.rollback()
            raise e


class BlockchainService:
    def __init__(self):
        self.api_url = current_app.config['TRON_API_URL']
        self.api_key = current_app.config['TRON_API_KEY']
        self.usdt_contract = current_app.config['USDT_CONTRACT_ADDRESS']

    def get_wallet_transactions(self, address, start_time=None):
        """
        Get TRC20 USDT transactions for a wallet address

        Args:
            address (str): Wallet address to check
            start_time (datetime): Optional start time to check from

        Returns:
            list: List of transactions
        """
        try:
            # If no start time provided, check last 1 hour
            if not start_time:
                start_time = datetime.utcnow() - timedelta(hours=1)

            # Convert to milliseconds timestamp
            min_timestamp = int(start_time.timestamp() * 1000)

            # Get transactions from Tron API
            response = requests.get(
                f"{self.api_url}/v1/accounts/{address}/transactions/trc20",
                params={
                    'only_to': True,  # Only incoming transactions
                    'contract_address': self.usdt_contract,
                    'min_timestamp': min_timestamp,
                    'limit': 50  # Adjust based on your needs
                },
                headers={
                    'TRON-PRO-API-KEY': self.api_key
                }
            )

            if not response.ok:
                current_app.logger.error(f"Tron API error: {response.text}")
                return []

            transactions = response.json().get('data', [])

            # Filter and format transactions
            formatted_transactions = []
            for tx in transactions:
                if tx.get('token_info', {}).get('symbol') != 'USDT':
                    continue

                formatted_transactions.append({
                    'hash': tx['transaction_id'],
                    'from_address': tx['from'],
                    'to_address': tx['to'],
                    'value': int(tx['value']),  # Already in smallest unit
                    'timestamp': tx['block_timestamp'],
                    'confirmations': self._get_confirmations(tx['block_number'])
                })

            return formatted_transactions

        except Exception as e:
            current_app.logger.error(f"Error getting transactions: {str(e)}")
            return []

    def _get_confirmations(self, block_number):
        """Get number of confirmations for a block"""
        try:
            # Get current block number
            response = requests.get(
                f"{self.api_url}/v1/blocks/latest",
                headers={'TRON-PRO-API-KEY': self.api_key}
            )

            if response.ok:
                latest_block = response.json()['block_header']['raw_data']['number']
                return latest_block - block_number
            return 0
        except:
            return 0

# scheduler/tasks.py
def process_deposits():
    """Process pending deposits"""
    blockchain_service = BlockchainService()

    # Get active assignments
    active_assignments = WalletAssignment.query.filter(
        WalletAssignment.is_active == True,
        WalletAssignment.expires_at > datetime.utcnow()
    ).all()

    for assignment in active_assignments:
        # Get transactions since assignment
        transactions = blockchain_service.get_wallet_transactions(
            assignment.wallet.address,
            start_time=assignment.assigned_at
        )

        for txn in transactions:
            # Skip if already processed
            if Transaction.query.filter_by(blockchain_txn_id=txn['hash']).first():
                continue

            # Verify transaction
            if txn['confirmations'] < current_app.config['MIN_CONFIRMATIONS']:
                continue

            try:
                amount = float(txn['value']) / 1e6

                # Create transaction record
                transaction = Transaction(
                    user_id=assignment.user_id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount_usdt=amount,
                    status=TransactionStatus.COMPLETED,
                    blockchain_txn_id=txn['hash'],
                    from_address=txn['from_address'],
                    to_address=txn['to_address'],
                    completed_at=datetime.fromtimestamp(txn['timestamp'] / 1000)
                )

                # Update user balance
                user = User.query.get(assignment.user_id)
                user.wallet_balance += amount

                db.session.add(transaction)
                db.session.commit()

                # Log success
                current_app.logger.info(
                    f"Deposit processed: {amount} USDT for user {user.id}"
                )

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(
                    f"Error processing deposit: {str(e)}"
                )


def cleanup_assignments():
    """Cleanup expired assignments"""
    expired = WalletAssignment.query.filter(
        WalletAssignment.is_active == True,
        WalletAssignment.expires_at <= datetime.utcnow()
    ).all()

    for assignment in expired:
        try:
            # Release wallet
            assignment.is_active = False
            assignment.wallet.status = WalletStatus.AVAILABLE
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error cleaning up assignment {assignment.id}: {str(e)}"
            )