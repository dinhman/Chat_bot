from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import subprocess
import os
import signal
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '6JMdyv3ArPvBbQkX'

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Set the login view

# Simulated user database (you should replace this with your actual user management system)
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

# Example user
users = {'admin': User('admin', 'admin')}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

socketio = SocketIO(app)

process = None

@app.route('/')
@login_required  # Require login for the index page
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required  # Require login for logout
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('start_process')
@login_required  # Require login for socket actions
def start_process():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen(['python', 'main3.py'])
        emit('process_status', 'VID_BOT started.')
    else:
        emit('process_status', 'VID_BOT is already running.')

@socketio.on('stop_process')
@login_required  # Require login for socket actions
def stop_process():
    global process
    if process and process.poll() is None:
        os.kill(process.pid, signal.SIGTERM)
        process = None
        emit('process_status', 'VID_BOT stopped.')
    else:
        emit('process_status', 'No running process to stop.')

@socketio.on('restart_process')
@login_required  # Require login for socket actions
def restart_process():
    stop_process()
    start_process()

if __name__ == '__main__':
    socketio.run(app)
