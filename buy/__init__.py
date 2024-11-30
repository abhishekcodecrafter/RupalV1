from flask import Blueprint

buy_bp = Blueprint('buy', __name__)

from . import routes