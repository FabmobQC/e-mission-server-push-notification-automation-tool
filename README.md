# e-mission-server-push-notification-automation-tool

## Script to send notifications to users based on mobile type and the project they subscribed to

1. Execute script on each project passed as parameter python main.py --project-config-file carrefour_des_donnees.json
2. Fetch users from mongodb database on Stage_Profiles filtering on the project_name field check in english and french
3. Compare subcription date update_ts to today date and select day in notifications list 
and for each notification in the day in the time minus the current time is less then 1 hour then send notification


`--project-config-file example:`

```
    {
        "project_name": {
            "english": "project name in english",
            "fench": "nom du projet en francais"
        },
        "notifications": {
            0: {
                "day": 0,
                "hour": null,
                "title_fr": "🏁  Vous y êtes",
                "title_en": "🏁  Here you go",
                "message_fr": "Félicitations vous participez maintenant à l'expérimentation 'Carrefour des données' 😊 ",
                "message_en": "Congratulations you are part of 'Carrefour des données' experiment 😊 "
            },
            1: {
                "day": 1,
                "hour": 21,
                "title_fr": "📅  Jour 1",
                "title_en": "📅  Day 1",
                "message_fr": "Choisissez le mode 🚴 <200d>♀️ 🚋 🚶 <200d>♀️🚔  🚁  et motif 🤿 pour vos dé placements ",
                "message_en": "Choose the mode 🚴 <200d>♀️ 🚋 🚶 <200d>♀️🚔  🚁  and the purpose 🤿 for your trips"
            }
        }
        
    }
```

Create an .env file that contains the url to the server example:

```
{
        "url": "mongodb://DATABASE_USER:PASSWORD@HOST:27017/DATABASE_NAME"
}
```

