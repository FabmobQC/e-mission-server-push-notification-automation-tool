# Script to send notifications to users based on mobile type and the project they subscribed to

import json
from pymongo import MongoClient
from datetime import datetime
import argparse
import emission.net.ext_service.push.notify_usage as pnu
import uuid
import pytz


def fetch_users(db, project):
    return db.Stage_Profiles.find({"project_name": {"$in": [project["project_name"]["english"], project["project_name"]["french"]]}})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--projectconfigfile", required=True, help="Path to project notifications config json file")
    args = vars(ap.parse_args())
    

    env_file = open('conf/storage/db.conf')
    env = json.load(env_file)

    client = MongoClient(env["timeseries"]["url"])
    db = client.Stage_database

    with open(args["projectconfigfile"]) as project_file:
        project = json.load(project_file)
        users = fetch_users(db, project)

        timezone = pytz.timezone(project["timezone"])
        
        for user in users:

            delta = datetime.now()-user["update_ts"]

            try:
                for notification in project["notifications_day"][str(delta.days)]["notifications"]:
                    if (datetime.now(timezone).hour - int(notification["hour"])) == 0:
                        title = notification["title_fr"] if user["phone_lang"] == "fr" else notification["title_en"]
                        message = notification["message_fr"] if user["phone_lang"] == "fr" else notification["message_en"] 
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

        

if __name__ == "__main__":
    main()
