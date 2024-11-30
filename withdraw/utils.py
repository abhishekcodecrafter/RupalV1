import re
from tronapi import Tron

def validate_tron_address(address):
    """Validate TRON address format"""
    try:
        tron = Tron()
        return tron.isAddress(address)
    except:
        # Fallback to regex validation if tronapi fails
        return bool(re.match(r'^T[A-Za-z0-9]{33}$', address))
