from flask import Flask
app = Flask(__name__)
# Secret Key for flask_login use
app.secret_key = "SecretVerySecret"