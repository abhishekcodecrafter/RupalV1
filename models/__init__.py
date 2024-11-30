from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here to make them available when importing from models package
from .models import (
    User,
    UserStatus,
    Transaction,
    TransactionType,
    TransactionStatus,
    BankAccount,
    WithdrawalAddress,
    ReferralCommission,
    ReferralEarning,
    OTP,
    WalletStatus, WalletAssignment, PooledWallet
)


# Optionally, you can define helper functions that work with models
def init_db(app):
    """Initialize the database and create tables"""
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_admin_user(mobile, wallet_pin):
    """Helper function to create admin user"""
    admin = User(
        mobile=mobile,
        is_admin=True,
        status=UserStatus.ACTIVE
    )
    admin.set_wallet_pin(wallet_pin)
    db.session.add(admin)
    db.session.commit()
    return admin


def get_user_statistics(user_id):
    """Helper function to get user statistics"""
    stats = {
        'buy_volume': db.session.query(db.func.sum(Transaction.amount_usdt))
                      .filter_by(user_id=user_id, transaction_type=TransactionType.BUY,
                                 status=TransactionStatus.COMPLETED)
                      .scalar() or 0,

        'sell_volume': db.session.query(db.func.sum(Transaction.amount_usdt))
                       .filter_by(user_id=user_id, transaction_type=TransactionType.SELL,
                                  status=TransactionStatus.COMPLETED)
                       .scalar() or 0,

        'total_commission': db.session.query(db.func.sum(ReferralEarning.amount_usdt))
                            .filter_by(user_id=user_id)
                            .scalar() or 0,

        'direct_referrals': User.query.filter_by(referred_by=user_id).count()
    }
    return stats