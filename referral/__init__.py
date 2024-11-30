from flask import Blueprint

referral_bp = Blueprint('referral', __name__)

from . import routes