from flask import Flask, render_template, request, redirect, url_for, session
from flask_mqtt import Mqtt
from flask_dance.contrib.google import make_google_blueprint, google

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883

# Google OAuth Configuration
app.config['GOOGLE_OAUTH_CLIENT_ID'] = 'YOUR_GOOGLE_CLIENT_ID'
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = 'YOUR_GOOGLE_CLIENT_SECRET'
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/google_login")

mqtt = Mqtt(app)

# Dummy user credentials for login
users = {
    "admin": "password123"
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Credentials, Try Again"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Save the new user in the users dictionary (or better in a database)
        users[username] = password
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/plus/v1/people/me")
    assert resp.ok, resp.text
    return "You are logged in as: " + resp.json()["displayName"]

if __name__ == "__main__":
    app.run(debug=True)
