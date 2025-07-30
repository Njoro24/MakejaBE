from flask import Blueprint, request, jsonify
from mpesa import MpesaAuth

# Create payment blueprint
payment_bp = Blueprint('payment', __name__)

# Initialize M-Pesa
mpesa = MpesaAuth()

@payment_bp.route('/mpesa/get-token', methods=['GET'])
def get_mpesa_token():
    """Get M-Pesa access token"""
    token = mpesa.get_access_token()
    if token:
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "message": "Failed to get token"}), 400

@payment_bp.route('/mpesa/stk-push', methods=['POST'])
def mpesa_stk_push():
    """Initiate M-Pesa STK Push payment"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['phone', 'amount', 'account_reference', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing {field}"}), 400
    
    # Validate phone number format
    phone = data['phone'].strip()
    if not phone:
        return jsonify({"success": False, "message": "Phone number is required"}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount"}), 400
    
    # Initiate STK Push
    result = mpesa.stk_push(
        phone_number=phone,
        amount=amount,
        account_reference=data['account_reference'],
        transaction_desc=data['description']
    )
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@payment_bp.route('/mpesa/stk-query', methods=['POST'])
def mpesa_stk_query():
    """Query M-Pesa STK Push payment status"""
    data = request.get_json()
    
    # Validate required field
    if 'checkout_request_id' not in data:
        return jsonify({"success": False, "message": "Missing checkout_request_id"}), 400
    
    checkout_request_id = data['checkout_request_id'].strip()
    if not checkout_request_id:
        return jsonify({"success": False, "message": "checkout_request_id cannot be empty"}), 400
    
    # Query payment status
    result = mpesa.stk_query(checkout_request_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@payment_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa callback (webhook)"""
    data = request.get_json()
    
    # Log the callback for debugging
    print(f"M-Pesa Callback received: {data}")
    
    # Process the callback data here
    # This is where you'd update your database with payment status
    
    # Return success response to M-Pesa
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

# Additional payment routes can be added here
@payment_bp.route('/health', methods=['GET'])
def payment_health():
    """Payment service health check"""
    return jsonify({
        "service": "payment",
        "status": "healthy",
        "mpesa_configured": True
    })