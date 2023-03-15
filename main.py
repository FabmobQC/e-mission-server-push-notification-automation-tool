# Script to send notifications to users based on mobile type and the project they subscribed to

import json
from pymongo import MongoClient
from datetime import datetime
import argparse
import emission.net.ext_service.push.notify_usage as pnu
import uuid
import pytz
import requests


def fetch_users(db, project):
    return db.Stage_Profiles.find({"project_name": {"$in": [project["name_fr"], project["name_en"]]}})

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

def sendPushNotifications(timezone, user, delta, daily_notifications):
    try:
        for notification in daily_notifications:
            if notification["day"] == str(delta.days):
                if (datetime.now(timezone).hour - int(notification["display_time"][0:2])) == 0:

                    (title, message) = getTitleBodyTuple(notification, user["phone_lang"])

                    json_data = {
                        "title": title,
                        "message": message
                    }
                    response = pnu.send_visible_notification_to_users([user["user_id"]], title, message, json_data, False)
                    print(response)
                elif datetime.now().hours() - notification["hour"] > 0:
                    print("Notification already sent or cronjob was missed")
                else:
                    print("It's not time to send the notification")
    except:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--projectconfigendpoint", required=True, help="Path to project notifications config json file")
    args = vars(ap.parse_args())
    

    env_file = open('conf/storage/db.conf')
    env = json.load(env_file)

    client = MongoClient(env["timeseries"]["url"])
    db = client.Stage_database

    response = requests.get(args["projectconfigendpoint"])

    project = json.load(response)
    users = fetch_users(db, project)

    timezone = pytz.timezone(project["timezone"])
    
    for user in users:

        delta = datetime.now()-user["update_ts"]

        sendPushNotifications(timezone, user, delta, project["daily_notifications"])

        

if __name__ == "__main__":
    main()
