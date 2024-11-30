from flask import Blueprint

deposit_bp = Blueprint('deposit', __name__)

from . import routes