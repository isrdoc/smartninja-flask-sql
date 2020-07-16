from flask import Flask, render_template, request, redirect, url_for, make_response
from models.settings import db
from models.user import User
from models.topic import Topic
import hashlib
import uuid

app = Flask(__name__)
db.create_all()


def user_from_session_token():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return user


@app.route('/')
def index():
    user = user_from_session_token()

    return render_template("index.html", user=user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords don't match! Go back and try again."

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User.create(
            username=username,
            password_hash=password_hash
        )

        response = make_response(redirect(url_for('index')))
        response.set_cookie(
            "session_token",
            user.session_token,
            httponly=True,
            samesite='Strict'
        )

        return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "This user does not exist"
        else:
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())  # if password hashes match, create a session token
                db.add(user)
                db.commit()

                # save user's session token into a cookie
                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", user.session_token, httponly=True, samesite='Strict')

                return response
            else:
                return "Your password is incorrect!"


@app.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    if request.method == "GET":
        return render_template("topic_create.html")
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        user = user_from_session_token()

        if not user:
            return redirect(url_for('login'))

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
