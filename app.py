from flask import Flask, render_template

from admin.routes import admin_bp
from config import Config
from deposit import deposit_bp
from models import db
from auth.routes import auth_bp
from bank.routes import bank_bp
from buy.routes import buy_bp
from sell.routes import sell_bp
from withdraw.routes import withdraw_bp
from referral.routes import referral_bp
from dasboard.routes import dashboard_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(bank_bp, url_prefix='/bank')
    app.register_blueprint(buy_bp, url_prefix='/buy')
    app.register_blueprint(sell_bp, url_prefix='/sell')
    app.register_blueprint(withdraw_bp, url_prefix='/withdraw')
    app.register_blueprint(referral_bp, url_prefix='/referral')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(deposit_bp, url_prefix='/deposit')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
