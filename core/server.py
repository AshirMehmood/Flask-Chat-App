"""
This is the server for our chat room

The following example creates a server-side event handler for an unnamed event:

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

The above example uses string messages. Another type of unnamed events use JSON data:

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))


"""

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, logout_user, login_required
from core import db as orm
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
db.create_all()
db.session.commit()

# current session
session = orm.session


@app.route("/")
def home():
    return render_template("base.html")


# User auth
@login_manager.user_loader
def load_user(user_id):
    return orm.User.query.get(int(user_id))
 

@app.route("/login", methods=["GET", "POST"])
def login():
    render_template("login.html")
    if request.method == "POST":
        user = orm.User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password")
    return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        user_name = session.query(orm.User).filter((orm.User.username==username))
        print(user_name)
        if username == user_name:
            flash("username already taken !")
            return redirect(url_for("user_register"))
        else:
            pass_word = request.form["password"]
            email = request.form["email"]
            new_user = orm.User(username=username, password=pass_word, email=email)  
            try:
                session.add(new_user)
                session.commit()
            except ConnectionAbortedError:
                flash("Unable to register")
                return redirect(url_for("login"))
            return redirect(url_for("login"))
            



if __name__ == "__main__":
    socketio.run(app)