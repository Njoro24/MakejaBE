from flask import Flask, jsonify
import requests
import base64

app = Flask(__name__)

class MpesaAuth:
    def __init__(self):
        # Replace with your actual credentials
        self.consumer_key = "Bl0yLyomUFlqQJv36ou12oxNLDVpRE38iPUYZ5dXZbGruDel"
        self.consumer_secret = "o3G6DSjlMnlWDbxKGe7EEAwRTwabldnpuaApcI4bPjcllbOUV3PMAhkEyCyAQrtm"
        self.base_url = "https://sandbox.safaricom.co.ke"
        
        # Sandbox test credentials
        self.shortcode = "174379"
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        
    def get_access_token(self):
        """Get OAuth access token from M-Pesa"""
        try:
            print(f"Consumer Key: {self.consumer_key[:10]}...")
            print(f"Consumer Secret: {self.consumer_secret[:10]}...")
            
            # Create base64 encoded string
            key_secret = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(key_secret.encode()).decode()
            
            # Set headers
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            # Make request
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data['access_token']
            else:
                return None
                
        except Exception as e:
            print(f"Exception: {str(e)}")
            return None
    
    def generate_password(self):
        """Generate password for STK Push"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        try:
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "message": "Failed to get access token"}
            
            # Generate password and timestamp
            password, timestamp = self.generate_password()
            
            # Prepare request
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": "https://mydomain.com/callback",  # We'll update this later
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"STK Push Response: {response.status_code}")
            print(f"STK Push Text: {response.text}")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "message": response.text}
                
        except Exception as e:
            print(f"STK Push Exception: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def stk_query(self, checkout_request_id):
        """Query STK Push payment status"""
        try:
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "message": "Failed to get access token"}
            
            # Generate password and timestamp
            password, timestamp = self.generate_password()
            
            # Prepare request
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"Query Response: {response.status_code}")
            print(f"Query Text: {response.text}")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "message": response.text}
                
        except Exception as e:
            print(f"Query Exception: {str(e)}")
            return {"success": False, "message": str(e)}

# Initialize M-Pesa
mpesa = MpesaAuth()

@app.route('/')
def home():
    return "M-Pesa Test API Running!"

@app.route('/get-token', methods=['GET'])
def get_token():
    token = mpesa.get_access_token()
    if token:
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "message": "Failed to get token"}), 400

@app.route('/stk-push', methods=['POST'])
def stk_push():
    from flask import request
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['phone', 'amount', 'account_reference', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing {field}"}), 400
    
    # Initiate STK Push
    result = mpesa.stk_push(
        phone_number=data['phone'],
        amount=data['amount'],
        account_reference=data['account_reference'],
        transaction_desc=data['description']
    )
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/stk-query', methods=['POST'])
def stk_query():
    from flask import request
    data = request.get_json()
    
    # Validate required fields
    if 'checkout_request_id' not in data:
        return jsonify({"success": False, "message": "Missing checkout_request_id"}), 400
    
    # Query payment status
    result = mpesa.stk_query(data['checkout_request_id'])
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

if __name__ == '__main__':
    print("Starting M-Pesa Test Server...")
    app.run(debug=True, port=5001)