import requests
import base64
from datetime import datetime
import os

class MpesaAuth:
    def __init__(self):
        """Initialize M-Pesa authentication with consumer key and secret."""
        self.consumer_key = "Bl0yLyomUFlqQJv36ou12oxNLDVpRE38iPUYZ5dXZbGruDel"
        self.consumer_secret = "o3G6DSjlMnlWDbxKGe7EEAwRTwabldnpuaApcI4bPjcllbOUV3PMAhkEyCyAQrtm"
        self.base_url = "https://sandbox.safaricom.co.ke"  # Sandbox URL
        
        # Sandbox credentials 
        self.shortcode = "174379"  # Sandbox shortcode
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Sandbox passkey
        
    def get_access_token(self):
        """Get OAuth access token from M-Pesa"""
        try:
            # Create base64 encoded string of consumer key and secret
            key_secret = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(key_secret.encode()).decode()
            
            # Set headers
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            # Make request
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data['access_token']
            else:
                print(f"Error getting token: {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception getting token: {str(e)}")
            return None
    
    def generate_password(self):
        """Generate password for STK Push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
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
            
            # Format phone number (ensure it starts with 254)
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+254'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Prepare request headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": "https://yourdomain.com/callback",  # i will update this with the actual domain
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            # Make STK Push request
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('ResponseCode') == '0':
                    return {"success": True, "data": response_data}
                else:
                    return {"success": False, "message": response_data.get('errorMessage', 'STK Push failed')}
            else:
                return {"success": False, "message": f"Request failed: {response.text}"}
                
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
            
            # Prepare request headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            # Make query request
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                return {"success": True, "data": response_data}
            else:
                return {"success": False, "message": f"Query failed: {response.text}"}
                
        except Exception as e:
            print(f"Query Exception: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def format_phone_number(self, phone_number):
        """Format phone number to correct M-Pesa format (254XXXXXXXXX)"""
        # Remove any spaces or special characters
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Handle different formats
        if phone_number.startswith('0'):
            return '254' + phone_number[1:]
        elif phone_number.startswith('254'):
            return phone_number
        elif len(phone_number) == 9:  
            return '254' + phone_number
        else:
            return phone_number  