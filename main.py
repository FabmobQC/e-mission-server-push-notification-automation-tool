# Script to send notifications to users based on mobile type and the project they subscribed to

"""
1. Execute script on each project passed as parameter python main.py --project-config-file carrefour_des_donnees.json
2. Fetch users from mongodb database on Stage_Profiles filtering on the project_name field check in english and french
3. Compare subcription date update_ts to today date and select day in notifications list 
and for each notification in the day in the time minus the current time is less then 1 hour then send notification


--project-config-file example:
    {
        "project_name": {
            "english": "project name in english",
            "french": "nom du projet en francais"
        },
        "notifications_day": {
            0: {
                "day": 0,
                "notifications": [
                    {
                        "hour": null,
                        "title_fr": "🏁 Vous y êtes",
                        "title_en": "🏁 Here you go",
                        "message_fr": "Félicitations vous participez maintenant à l'expérimentation 'Carrefour des données' 😊",
                        "message_en": "Congratulations you are part of 'Carrefour des données' experiment 😊"
                    }
                ]
            },
            1: {
                "day": 1,
                "notifications": [
                    {
                        "hour": 21,
                        "title_fr": "📅  Jour 1",
                        "title_en": "📅  Day 1",
                        "message_fr": "Choisissez le mode 🚴 <200d>♀️ 🚋 🚶 <200d>♀️🚔  🚁  et motif 🤿 pour vos dé placements ",
                        "message_en": "Choose the mode 🚴 <200d>♀️ 🚋 🚶 <200d>♀️🚔  🚁  and the purpose 🤿 for your trips"
                    }
                ]
            }
        }
        
    }

"""

import json
from pymongo import MongoClient
from datetime import datetime
import argparse
import emission.net.ext_service.push.notify_usage as pnu

def fetch_users(db, project):
    return db.Stage_Profiles.find({"project_name": {"$in": [project["project_name"]["english"], project["project_name"]["french"]]}})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--projectconfigfile", required=True, help="Path to project notifications config json file")
    args = vars(ap.parse_args())
    

    env_file = open('.env')
    env = json.load(env_file)

    client = MongoClient(env["url"])
    db = client.Stage_database

    with open(args["projectconfigfile"]) as project_file:
        project = json.load(project_file)
        users = fetch_users(db, project)

        for user in users:
            delta = datetime.now()-user["update_ts"]
            try:
                print(str(delta.days)+"\n")
                for notification in project["notifications_day"][str(delta.days)]:
#                    import pdb
#                    pdb.set_trace()
                    if datetime.now().hours() - notification["hour"] == 0:
                        title = notification["title_fr"] if user["phone_lang"] == "fr" else notification["title_en"]
                        message = notification["message_fr"] if user["phone_lang"] == "fr" else notification["message_en"] 
                        json_data = {
                           "title": title,
                           "message": message
                        }
                        response = pnu.send_visible_notification_to_users([uuid.UUID(user["user_id"]),], title, message, json_data, False)
                        print(response)
                    elif datetime.now().hours() - notification["hour"] > 0:
                        print("Notification already sent or cronjob was missed")
                    else:
                        print("It's not time to send the notification")
            except:
                print("No nofitication found")

        

if __name__ == "__main__":
    main()
