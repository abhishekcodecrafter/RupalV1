import requests
from datetime import datetime, timedelta
from flask import current_app


def validate_trc20_transaction(txn_hash, expected_amount, to_address):
    """Verify TRC20 transaction using Tron API"""
    try:
        # Using Tron API to verify transaction
        api_url = f"{current_app.config['TRON_API_URL']}/v1/transactions/{txn_hash}"
        response = requests.get(api_url)
        print(response)

        if not response.ok:
            return False, "Unable to verify transaction"

        txn_data = response.json()

        # Validate transaction details
        if txn_data['type'] != 'Transfer':
            return False, "Invalid transaction type"

        if txn_data['to_address'] != to_address:
            return False, "Invalid recipient address"

        if float(txn_data['value']) != expected_amount:
            return False, "Amount mismatch"

        if txn_data['confirmations'] < current_app.config['MIN_CONFIRMATIONS']:
            return False, "Transaction not confirmed yet"

        # Check if transaction is recent (within last 24 hours)
        txn_time = datetime.fromtimestamp(txn_data['timestamp'] / 1000)
        if datetime.utcnow() - txn_time > timedelta(hours=24):
            return False, "Transaction too old"

        return True, None

    except Exception as e:
        return False, str(e)