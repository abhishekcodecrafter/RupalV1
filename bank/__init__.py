# bank/__init__.py
from flask import Blueprint

bank_bp = Blueprint('bank', __name__)

from . import routes