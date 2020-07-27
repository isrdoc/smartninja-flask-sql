from flask import render_template, request, redirect, url_for, Blueprint

from models.settings import db
from models.topic import Topic
from models.user import User
from models.comment import Comment

from utils.redis_helper import set_csrf_token, is_valid_csrf
from utils.auth_helper import user_from_session_token

comment_handlers = Blueprint("comment", __name__)


@comment_handlers.route("/topic/<topic_id>/create-comment", methods=["POST"])
def comment_create(topic_id):
    user = user_from_session_token()

    if not user:
        return redirect(url_for('auth.login'))

    csrf = request.form.get("csrf")

    if not is_valid_csrf(csrf, user.username):
        return "CSRF token is not valid!"

    text = request.form.get("text")
    topic = Topic.read(topic_id)

    Comment.create(topic=topic, text=text, author=user)

    return redirect(url_for('topic.topic_details', topic_id=topic_id))
