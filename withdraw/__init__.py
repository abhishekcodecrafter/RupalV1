from flask import Blueprint

withdraw_bp = Blueprint('withdraw', __name__)

from . import routes