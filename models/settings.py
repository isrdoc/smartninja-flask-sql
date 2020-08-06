import os
from sqla_wrapper import SQLAlchemy

db = None


def init_db():
    global db
    if not db:
        db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))

    return db


if __name__ == '__main__':
    init_db()
