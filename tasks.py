import os
import random
import json
import requests

from huey import RedisHuey

# worker
huey = RedisHuey(url=os.getenv('REDIS_URL'))


# task
@huey.task(retries=5, retry_delay=5)
def get_random_num():
    print("This is a task to get a random number")
    num = random.randint(1, 3)
    print("Random number is {}".format(num))

    if num == 1:
        return True
    else:
        raise Exception("Error in the worker... :(")


@huey.task(retries=10, retry_delay=600)
def send_email_task(receiver_email, subject, text):
    sender_email = os.getenv("MY_SENDER_EMAIL")  # Your website's official email address
    api_key = os.getenv('SENDGRID_API_KEY')

    if not sender_email or not api_key:
        print("No env vars or no email address.")
        print("The email was not sent.")
        print("If it was sent, this would be the subject: {}".format(subject))
        print("This would be the text: {}".format(text))
        print("And this would be the receiver: {}".format(receiver_email))
        return

    url = "https://api.sendgrid.com/v3/mail/send"

    data = {"personalizations": [{
                "to": [{"email": receiver_email}],
                "subject": subject
            }],

            "from": {"email": sender_email},

            "content": [{
                "type": "text/plain",
                "value": text
            }]
    }

    headers = {
        'authorization': "Bearer {0}".format(api_key),
        'content-type': "application/json"
    }

    response = requests.request("POST", url=url, data=json.dumps(data), headers=headers)

    print("Sent to SendGrid")
    print(response.text)

    response_data = json.loads(response.text)

    if response_data["errors"]:
        print(response_data["errors"][0]["message"])
        raise Exception("Error in SendGrid")
