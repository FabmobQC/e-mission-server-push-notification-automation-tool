# e-mission-server-push-notification-automation-tool


## How to use this tool

This tool needs to be clone in e-mission-server/bin folder on e-mission-server (https://github.com/e-mission/e-mission-server)

Once setup, the tool can be called from a script that pulls configuration data from the corresponding endpoints for each project. The input for this script is a file containing a list of configuration endpoints.

```
#!/bin/bash

APPROOT=/root

# First sync user's projects

cd $APPROOT/wp_form-import-user-project-to-mongodb

python main.py

# Send push notifications

cd $APPROOT/e-mission-server/

source setup/activate.sh

File=$1

Lines=$(cat $File)

for Line in $Lines
do
	echo "Sending notification to $Line"
	./e-mission-py.bash bin/e-mission-server-push-notification-automation-tool/main.py -p $Line 
done

```

## Configuration endpoints

Projects configuration is handled by the E-mission backend project that returns configurations for each projects. See https://github.com/FabmobQC/e-mission-backend


## Important

The script should be executed once a day to avoid sending notifications multiple times per day.

## How does the script works:

The script send notifications to users based on their device type iOS or Android. Moreover the script sends emails using an email service. 
We configured in our example Mailchimp.

1. Execute script on each project passed as parameter python main.py --project-config-endpoint
2. Fetch users from mongodb database on Stage_Profiles filtering on the project_name field check in english and french
3. Compare subcription date update_ts to today date and select day in notifications list 
and for each notification in the day in the time minus the current time is less then 1 hour then send notification


`Example of what should the endpoint return:`

```
{
    "id": 1,
    "main_form": {
        "id": 1,
        "urls": [
            {
                "id": 1,
                "language": "fr",
                "url": "https://projectwebsite.com/fr/form"
            },
            {
                "id": 2,
                "language": "en",
                "url": "https://projectwebsite.com/en/form"
            }
        ],
        "is_active": true,
        "day": 0,
        "display_time": "00:00:00"
    },
    "daily_forms": [
        {
            "id": 1,
            "urls": [
                {
                    "id": 1,
                    "language": "fr",
                    "url": "https://projectwebsite.com/fr/dailyform"
                },
                {
                    "id": 2,
                    "language": "en",
                    "url": "https://projectwebsite.com/en/dailyform"
                }
            ],
            "is_active": true,
            "day": 0,
            "display_time": "00:00:00"
        }
    ],
    "daily_notifications": [
        {
            "id": 1,
            "titles": [
                {
                    "id": 1,
                    "language": "fr",
                    "title": "🏁  Vous y êtes"
                },
                {
                    "id": 2,
                    "language": "en",
                    "title": "🏁  Here you go"
                }
            ],
            "messages": [
                {
                    "id": 1,
                    "language": "fr",
                    "body": "Félicitations vous participez maintenant à l'expérimentation 'Carrefour des données' 😊"
                },
                {
                    "id": 2,
                    "language": "en",
                    "body": "Congratulations you are part of 'Carrefour des données' experiment 😊"
                }
            ],
            "day": 0,
            "display_time": "15:00:00"
        }
    ],
    "timezone": "America/Montreal",
    "name_fr": "Nom du projet en francais",
    "name_en": "English project name",
    "server_url": "https://api.projectwebsite.com/",
    "daily_emails": [],
    "modes": [],
    "purposes": []
}
```

Create an .env file that contains the url to the server example or point to main e-mission config file `conf/storage/db.conf`:

```
{
        "url": "mongodb://DATABASE_USER:PASSWORD@HOST:27017/DATABASE_NAME"
}
```

## Sending Transactional emails with Mailchimp api with Python

https://mailchimp.com/developer/transactional/guides/send-first-email/


```
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

mailchimp = MailchimpTransactional.Client('YOUR_API_KEY')
message = {
    "from_email": "manny@mailchimp.com",
    "subject": "Hello world",
    "text": "Welcome to Mailchimp Transactional!",
    "to": [
      {
        "email": "freddie@example.com",
        "type": "to"
      }
    ]
}

def run():
  try:
    response = mailchimp.messages.send({"message":message})
    print('API called successfully: {}'.format(response))
  except ApiClientError as error:
    print('An exception occurred: {}'.format(error.text))

run()
```