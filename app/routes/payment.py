from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.payment import Payment
from app.db import db
import requests
import base64
from datetime import datetime
import os

payment_bp = Blueprint('payment', __name__)

# M-Pesa Configuration (use environment variables)
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')

def get_mpesa_token():
    """Get M-Pesa access token"""
    try:
        api_url = "https://sandbox-api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        # Encode credentials
        credentials = base64.b64encode(f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_url, headers=headers)
        return response.json().get('access_token')
    except Exception as e:
        print(f"Token error: {str(e)}")
        return None

@payment_bp.route('/mpesa/stk-push', methods=['POST'])
@jwt_required()
def mpesa_stk_push():
    """Initiate M-Pesa STK Push"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate input
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        description = data.get('description', 'Payment')
        
        if not phone_number or not amount:
            return jsonify({'error': 'Phone number and amount required'}), 400
        
        # Format phone number (remove + and ensure 254 prefix)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        # Get access token
        token = get_mpesa_token()
        if not token:
            return jsonify({'error': 'Failed to get M-Pesa token'}), 500
        
        # Create payment record
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency='KES',
            payment_method='mpesa',
            phone_number=phone_number,
            description=description,
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()
        
        # Prepare STK Push request
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
        
        stk_push_data = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{MPESA_CALLBACK_URL}/api/payments/mpesa/callback",
            "AccountReference": payment.id,
            "TransactionDesc": description
        }
        
        # Make STK Push request
        api_url = "https://sandbox-api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=stk_push_data, headers=headers)
        response_data = response.json()
        
        if response_data.get('ResponseCode') == '0':
            # Update payment with checkout request ID
            payment.mpesa_checkout_request_id = response_data.get('CheckoutRequestID')
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'STK Push sent successfully',
                'payment_id': payment.id,
                'checkout_request_id': response_data.get('CheckoutRequestID')
            }), 200
        else:
            payment.status = 'failed'
            db.session.commit()
            return jsonify({
                'error': 'STK Push failed',
                'message': response_data.get('errorMessage', 'Unknown error')
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """M-Pesa callback endpoint"""
    try:
        data = request.get_json()
        
        # Extract callback data
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        # Find payment by checkout request ID
        payment = Payment.query.filter_by(mpesa_checkout_request_id=checkout_request_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract receipt number
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')
                    break
            
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
        else:
            # Payment failed
            payment.status = 'failed'
        
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return jsonify({'error': 'Callback processing failed'}), 500

@payment_bp.route('/status/<payment_id>', methods=['GET'])
@jwt_required()
def payment_status(payment_id):
    """Check payment status"""
    try:
        user_id = get_jwt_identity()
        payment = Payment.query.filter_by(id=payment_id, user_id=user_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify(payment.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    """Get user payment history"""
    try:
        user_id = get_jwt_identity()
        payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
        
        return jsonify([payment.to_dict() for payment in payments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/health', methods=['GET'])
def payment_health():
    """Payment service health check"""
    return jsonify({
        'service': 'payment',
        'status': 'healthy',
        'mpesa_configured': bool(MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET)
    }), 200