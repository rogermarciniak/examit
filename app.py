import os

import flask_admin as admin
import flask_login as login
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

from user import User
from views import AdminIndexView, BlankView

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# bower_components
@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory(os.path.join(app.root_path,
                                            'bower_components'), path)


@app.route('/dist/<path:path>')
def send_dist(path):
    return send_from_directory(os.path.join(app.root_path, 'dist'), path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.join(app.root_path, 'js'), path)


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)


# Flask views
@app.route('/')
def index():
    return render_template("sb-admin/redirect.html")


@app.route('/student/')
def student():
    return render_template("sb-admin/student.html")


@app.errorhandler(404)
def fourOhFour(error):
    return '404: You have wandered too far young adventurer!'


# Initialize flask-login
init_login()


# Create admin
admin = admin.Admin(app,
                    'ExamIT v0.8',
                    index_view=AdminIndexView())
# admin.add_view(BlankView(name='Blank', url='blank', endpoint='blank'))

if __name__ == '__main__':
    app.run(debug=True, port=5050)
