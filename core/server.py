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
from forms import LoginForm, RegistrationForm
import requests
from gen_link import gen_link



# app = Flask(__name__)
# db.init_app(app)


app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager(app)


# current session
session = db.session



@app.route("/")
def home():
    """
    Default view
    """
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
    """
    Login view
    """
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
        # checks if the query was succesfull and checks the loaded column's password hash
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
    """
    Logout view
    """
    logout_user()
    return redirect(url_for("home"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Dashboard view, is accessible after successful register/login
    """
    return render_template("dashboard.html")


@app.route("/register", methods=["GET", "POST"])
def user_register():
    """
    register view
    """
    form = RegistrationForm() # class's instance is mapped to form page' data now
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "GET":
        flash("Entered in the GET request")
        return render_template("register.html", form=form)
    if request.method == "POST":
        flash("Entered in the POST request")
        if form.validate_on_submit():
            new_user = orm.User(username=form.username.data,
                                password=form.password.data, email=form.email.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

        # username = request.form["username"]
        # user_name = db.session.query(orm.User).filter((orm.User.username==username))
        # flash(user_name)
        # if user_name:
        #     flash("username already taken !")
        #     return redirect(url_for("user_register"))
        # else:
        #     pass_word = request.form["password"]
        #     # password checks
            
        #     email = request.form["email"]
        #     new_user = orm.User(username=username, password=pass_word, email=email)
        #     try:
        #         db.session.add(new_user)
        #         db.session.commit()
        #     except ConnectionAbortedError:
        #         flash("Unable to register")
        #         return redirect(url_for("user_register"))
        #     return redirect(url_for("login"))     


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_room():
    if request.method == "GET":
        return render_template("create-room.html")
    else: # some error returns 400 on POST
        room_name = request.form["roomname"]
        # external image server
        flash("continuing the post req")
        #third_party_url = "https://api.imgbb.com/1/upload?expiration=600&key=232a019e6eebdad639ac9080d8897172/" + request.form["banner"]
        #banner_url = requests.post(third_party_url)
        # api response in JSON, we need to parse and get url
        banner_url = "empty"
        # generating unique url for the room
        domain = "http://127.0.0.1/" + gen_link()
        new_room = orm.Room(room_name, banner_url, domain, orm.User)
        current_user.admin_status = True
        db.session.add(new_room)
        db.session.commit()
        new_room.users.insert(current_user)
        db.session.commit()
        return redirect(url_for("dashboard"))





@app.route("/join", methods=["GET", "POST"])
@login_required
def join_room():
    if request.method == "GET":
        return render_template("join-room.html")
    url = request.form["url"]
    room = db.session.scalar(
        s.select(orm.Room).where(url == orm.Room.room_name)
    )
    if room is not None:
        orm.Room.users.append(current_user)
        flash(f"successfully joined {room.room_name}")
        return redirect(url_for("dashboard"))
    else:
        flash("Room does not exist !")
        return redirect(url_for("join_room"))


@app.route("/message_room/<detail>", methods=["GET", "POST"])
@login_required
def open_room(detail):
    if request.method == "GET":
        return render_template("message-room.html")



if __name__ == "__main__":
    socketio.run(app)
