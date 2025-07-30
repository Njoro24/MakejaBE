from flask import current_app
from flask_mail import Message, Mail
import os

class EmailService:
    @staticmethod
    def send_verification_email(user_email, user_name, token):
        """Send email verification email"""
        try:
            frontend_url = current_app.config['FRONTEND_URL']
            verification_url = f"{frontend_url}/verify-email?token={token}"
            
            # Get mail instance from current_app
            mail = current_app.extensions['mail']
            
            msg = Message(
                subject='Verify Your Email - Makeja Hostel App',
                recipients=[user_email],
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            msg.html = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                        .button {{ display: inline-block; background: #007bff; color: white; 
                                  padding: 15px 30px; text-decoration: none; border-radius: 5px; 
                                  font-weight: bold; margin: 20px 0; }}
                        .footer {{ color: #666; font-size: 14px; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to Makeja!</h1>
                            <p>Verify your email to get started</p>
                        </div>
                        <div class="content">
                            <h2>Hello {user_name}!</h2>
                            <p>Thank you for registering with Makeja Hostel App. To complete your registration and start booking hostels, please verify your email address.</p>
                            
                            <div style="text-align: center;">
                                <a href="{verification_url}" class="button">Verify Email Address</a>
                            </div>
                            
                            <div class="footer">
                                <p><strong>This link will expire in 24 hours.</strong></p>
                                <p>If you didn't create an account with us, please ignore this email.</p>
                                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                                <p style="word-break: break-all; color: #007bff;">{verification_url}</p>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user_email, user_name, reset_url):
        """Send password reset email (bonus feature)"""
        try:
            # Get mail instance from current_app
            mail = current_app.extensions['mail']
            
            msg = Message(
                subject='Reset Your Password - Makeja',
                recipients=[user_email],
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            msg.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1>Password Reset Request</h1>
                        <p>Hello {user_name},</p>
                        <p>You requested a password reset. Click the link below to reset your password:</p>
                        <p><a href="{reset_url}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                        <p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>
                    </div>
                </body>
            </html>
            """
            
            mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending password reset email: {str(e)}")
            return False