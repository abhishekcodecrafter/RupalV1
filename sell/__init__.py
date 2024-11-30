from flask import Blueprint

sell_bp = Blueprint('sell', __name__)

from . import routes