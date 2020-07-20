from flask import Flask, render_template, request, redirect, url_for, make_response
from models.settings import db
from models.user import User
from models.topic import Topic
import hashlib
import uuid
import os
import smartninja_redis

redis = smartninja_redis.from_url(os.environ.get("REDIS_URL"))

app = Flask(__name__)
db.create_all()


def user_from_session_token():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return user


def set_csrf_token(user):
    csrf_token = str(uuid.uuid4())
    redis.set(name=csrf_token, value=user.username)

    return csrf_token


@app.route('/')
def index():
    user = user_from_session_token()

    topics = db.query(Topic).all()

    return render_template("index.html", user=user, topics=topics)


@app.route("/logout")
def logout():
    user = user_from_session_token()

    user.session_token = ""
    db.add(user)
    db.commit()

    return redirect(url_for('index'))


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
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(user=user)

        return render_template("topic_create.html", csrf_token=csrf_token)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        csrf = request.form.get("csrf")

        redis_csrf_username = None
        redis_csrf_username_hex = redis.get(name=csrf)
        if redis_csrf_username_hex:
            redis_csrf_username = redis_csrf_username_hex.decode()

        if not user:
            return redirect(url_for('login'))

        if not redis_csrf_username and redis_csrf_username != user.username:
            return "CSRF token is not valid!"

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for('index'))


@app.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    user = user_from_session_token()

    return render_template("topic_details.html", topic=topic, user=user)


@app.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(user)

        return render_template("topic_edit.html", topic=topic, csrf_token=csrf_token)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()

            return redirect(url_for('topic_details', topic_id=topic_id))


if __name__ == '__main__':
    app.run()
