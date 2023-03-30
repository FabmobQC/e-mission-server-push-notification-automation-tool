# Script to send notifications to users based on mobile type and the project they subscribed to

import json
from pymongo import MongoClient
from datetime import datetime
import argparse
import emission.net.ext_service.push.notify_usage as pnu
import pytz
import requests

import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

def get_users(db, project):

    return db.Stage_Profiles.find({
        "$or": [
            {"project_id": {"$eq": project["id"]}},
            {"project_name": {"$in": [project["name_fr"], project["name_en"]]}},
        ]
    })

def getTitleBodyTuple(notification, language):
    title = ""
    body = ""
    for element in notification["titles"]:
        if element["language"] == language:
            title = element["title"]
    for element in notification["messages"]:
        if element["language"] == language:
            body = element["body"]
    return (title, body)

def sendPushNotifications(user, now_datetime, project_day, daily_notifications):
    try:
        for notification in daily_notifications:
            if notification["day"] == project_day:
                if now_datetime.hour == int(notification["display_time"][0:2]):

                    (title, message) = getTitleBodyTuple(notification, user["phone_lang"])

                    json_data = {
                        "title": title,
                        "message": message
                    }
                    response = pnu.send_visible_notification_to_users([user["user_id"]], title, message, json_data, False)
                    print(response)
                elif now_datetime.hours() - notification["hour"] > 0:
                    print("Notification already sent or cronjob was missed")
                else:
                    print("It's not time to send the notification")
    except:
        pass

def sendEmail(user, now_datetime, project_day, daily_emails, from_email, mailchimp):
    try:
        for email in daily_emails:
            if email["day"] == project_day:
                if now_datetime.hour == int(email["display_time"][0:2]):

                    (title, message) = getTitleBodyTuple(email, user["phone_lang"])

                    message = {
                        "from_email": from_email,
                        "subject": title,
                        "text": message,
                        "to": [
                        {
                            "email": user["email"],
                            "type": "to"
                        }
                        ]
                    }
                    try:
                        response = mailchimp.messages.send({"message":message})
                        print('API called successfully: {}'.format(response))
                    except ApiClientError as error:
                        print('An exception occurred: {}'.format(error.text))
                elif datetime.now().hours() - email["hour"] > 0:
                    print("Email already sent or cronjob was missed")
                else:
                    print("It's not time to send the email")
    except:
        pass

def main():
    # get project config
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--projectconfigendpoint", required=True, help="Path to project notifications config json file")
    args = vars(ap.parse_args())
    response = requests.get(args["projectconfigendpoint"])
    project = response.json()
    
    # get users
    env_file = open('conf/storage/db.conf')
    env = json.load(env_file)
    client = MongoClient(env["timeseries"]["url"])
    db = client.Stage_database
    users = get_users(db, project)

    # mailchimp = MailchimpTransactional.Client(env["MAILCHIMP_API_KEY"])

    timezone = pytz.timezone(project["timezone"])
    now_datetime = datetime.now().astimezone(timezone)

    for user in users:
        # Get project day
        creation_ts = user["creation_ts"].replace('Z', '+00:00') # fromisoformat does not support 'Z' until Python 3.11
        creation_datetime = datetime.fromisoformat(creation_ts).astimezone(timezone)
        delta = now_datetime.date() - creation_datetime.date()
        project_day = delta.days

        sendPushNotifications(user, now_datetime, project_day, project["daily_notifications"])

        #sendEmail(timezone, user, delta, project["daily_emails"], env["from_email"], mailchimp)

if __name__ == "__main__":
    main()

