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
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import models as orm
from models import app, db
import sqlalchemy as s
from urllib.parse import urlsplit
from forms import LoginForm



# app = Flask(__name__)
# db.init_app(app)


app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager(app)


# current session
session = db.session



@app.route("/")
def home():
    return render_template("base.html")


# User auth
@login_manager.user_loader
def load_user(user_id):
    try:
        return orm.User.query.get(user_id)
    except:
        return None


@app.route("/login", methods=["GET", "POST"])
def login():
    # if current_user.is_authenticaed:
    #     return redirect(url_for("dashboard"))
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "GET":
        return render_template("login.html", form=form)
    if request.method == "POST":
        # this query loads the whole column -> class instance of matching username
        user = db.session.scalar(
            s.select(orm.User).where(orm.User.username == form.username.data)

        )
        # checks if the query was succesfull and checks the loaded columns password hash
        # with input password, if they match, means user is valid, creds are matching
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data) 
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(url_for("dashboard"))
        # the login system is working now

        # password_check = orm.User.check_password(request.form["password"])
        # user = db.session.query(orm.User).filter_by(
        # orm.User.username.like(request.form["username"]),
        # orm.User.password.like())
        # if user:
        #     password = orm.User.query.filter_by(password=password_check).first()

        # if user exists, fetch the password hash in the same row as the  
        # username, pass that hash to check password method along with
        # the entered password during login, if check_password() returns
        # true, login the user
        # if user == request.form["username"] and password == request.form["password"]:
        #     login_user(user, remember=user)
        #     return redirect(url_for("dashboard"))
        #flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


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
        user_name = db.session.query(orm.User).filter((orm.User.username==username))
        flash(user_name)
        if user_name:
            flash("username already taken !")
            return redirect(url_for("user_register"))
        else:
            pass_word = request.form["password"]
            # password checks
            
            email = request.form["email"]
            new_user = orm.User(username=username, password=pass_word, email=email)
            try:
                db.session.add(new_user)
                db.session.commit()
            except ConnectionAbortedError:
                flash("Unable to register")
                return redirect(url_for("user_register"))
            return redirect(url_for("login"))        


if __name__ == "__main__":
    socketio.run(app)