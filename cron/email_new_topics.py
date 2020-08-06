import datetime

from models.settings import init_db
db = init_db()

from models.topic import Topic
from models.user import User

from utils.email_helper import send_email


def new_topics_email():
    print("Cron job: New topics daily email")

    # find all topics created in the last 24 hours
    yesterday_topics = db.query(Topic).filter(Topic.created > (datetime.datetime.now() - datetime.timedelta(days=1))).all()

    print(yesterday_topics)

    # if no topics, finish the task without sending the email
    if not yesterday_topics:
        print("No new topics created yesterday, so no email will be sent.")
        return

    # create an email message
    message = "Topics created yesterday:\n"

    for topic in yesterday_topics:
        message += f"- {topic.title}\n"  # add every new topic title in the email message

    print(message)  # print message in the console

    users = db.query(User).all()  # get all users from the database

    for user in users:
        if user.email_address:  # if user has email address, send her/him an email
            send_email(
                receiver_email=user.email_address,
                subject="See new topics at Ninja Tech Forum",
                text=message
            )


if __name__ == '__main__':
    new_topics_email()
