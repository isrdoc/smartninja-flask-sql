from flask import render_template, request, redirect, url_for, Blueprint
import os

from models.settings import db
from models.topic import Topic
from models.comment import Comment

from utils.redis_helper import set_csrf_token, is_valid_csrf
from utils.auth_helper import user_from_session_token

topic_handlers = Blueprint("topic", __name__)


@topic_handlers.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(username=user.username)

        return render_template("topic/create.html", csrf_token=csrf_token)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        csrf = request.form.get("csrf")

        if not user:
            return redirect(url_for('login'))

        if not is_valid_csrf(csrf=csrf, username=user.username):
            return "CSRF token is not valid!"

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for('index'))


@topic_handlers.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    user = user_from_session_token()
    topic = Topic.read(topic_id)
    comments = Comment.read_all(topic)
    csrf_token = set_csrf_token(username=user.username)

    # START test background tasks (TODO: delete this code later)
    if os.getenv('REDIS_URL'):
        from tasks import get_random_num
        get_random_num()
    # END test background tasks

    return render_template(
        "topic/details.html",
        topic=topic,
        user=user,
        comments=comments,
        csrf_token=csrf_token
    )


@topic_handlers.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    user = user_from_session_token()

    if request.method == "GET":
        csrf_token = set_csrf_token(username=user.username)

        return render_template("topic/edit.html", topic=topic, csrf_token=csrf_token)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:
            Topic.update(topic_id, title, text)

            return redirect(url_for('topic.topic_details', topic_id=topic_id))
