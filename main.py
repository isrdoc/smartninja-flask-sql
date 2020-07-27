from flask import Flask, render_template

from models.settings import db
from models.topic import Topic

from handlers.auth import auth_handlers
from handlers.topic import topic_handlers
from handlers.comment import comment_handlers

from utils.auth_helper import user_from_session_token

app = Flask(__name__)

app.register_blueprint(auth_handlers)
app.register_blueprint(topic_handlers)
app.register_blueprint(comment_handlers)

db.create_all()


@app.route('/')
def index():
    user = user_from_session_token()
    topics = db.query(Topic).all()

    return render_template("index.html", user=user, topics=topics)


if __name__ == '__main__':
    app.run()
