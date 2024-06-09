from flask import Flask, render_template, request, redirect, url_for, session, make_response
import pyotp
import qrcode
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# W rzeczywistej aplikacji użyj bazy danych do przechowywania danych użytkowników i sekretnych kluczy
users = {
    'user1': {
        'password': 'password123',
        'secret': pyotp.random_base32()
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('setup'))  # Zmieniono przekierowanie na 'setup'
        else:
            return 'Invalid username or password'
    
    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    
    if request.method == 'POST':
        token = request.form['token']
        totp = pyotp.TOTP(user['secret'])
        
        if totp.verify(token):
            session['authenticated'] = True
            return redirect(url_for('protected'))
        else:
            return 'Invalid token'
    
    return render_template('verify.html')

@app.route('/protected')
def protected():
    if 'authenticated' in session:
        return 'Logged in successfully!'
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/qrcode')
def qrcode_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]
    totp = pyotp.TOTP(user['secret'])
    uri = totp.provisioning_uri(name=username, issuer_name='MyApp')
    
    # Generate QR code
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    response = make_response(buf.read())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route('/setup')
def setup():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('setup.html')

if __name__ == '__main__':
    app.run(debug=True)