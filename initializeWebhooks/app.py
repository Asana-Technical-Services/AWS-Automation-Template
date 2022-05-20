"""
initializeWebhooks/app.py
Lambda Function that initializes the connections for this automation
"""
import os
import json
import secrets
import webhooks
import urllib.parse
from asana_client import Asana_Client

### overall flow:
## add listeners to main portfolio
## add listeners to each project in main portfolio for CF changes


def lambda_handler(event, context):

    resourceID = os.environ["API_RESOURCE"]
    # regionID = os.environ["API_REGION"]
    regionID = "us-west-1"

    domain = f"https://{resourceID}.execute-api.{regionID}.amazonaws.com/Prod"

    # Init
    projects_portfolio_gid = None
    signature = None
    bot_secrets = None
    api_key = None

    # Retrieve environment variables
    try:
        projects_portfolio_gid = os.environ["PROJECTS_PORTFOLIO_GID"]
    except:
        print("x-hook-secret does not exist")

    try:
        bot_secret_arn = os.environ["BOT_SECRET_ARN"]
    except:
        print(
            "BOT_SECRET_ARN not set. please set it in the cloudformation project template.yaml and try again."
        )
        return

    try:
        bot_secrets = secrets.get_secret_value(bot_secret_arn)
        api_key = bot_secrets["API_KEY"]
    except:
        print(
            "Could not access Asana secret keys. Check that they are set in Secrets Manager"
        )
        return

    asana = Asana_Client(api_key)

    # clean up any existing webhooks to ensure we do not have duplicate or unnecessary webhooks set
    webhooks.delete_active_webhooks(asana)

    print("deleted all active webhooks.")

    # update the secret object to remove any stored webhook data
    new_bot_secrets = {"API_KEY": api_key}
    secrets.update_secret(bot_secret_arn, json.dumps(new_bot_secrets))

    # create a new webhook for the projects portfolio
    webhooks.set_portfolio_webhook(projects_portfolio_gid, domain, asana)

    # get all projects from the portfolio
    projects = []
    url = f"portfolios/{projects_portfolio_gid}/items"

    projects_result = asana.request("GET", url)

    if not projects_result["success"]:
        print("get portfolio items failed")
        return

    projects = projects_result["data"]

    for item in projects:
        print(item)
        if item["resource_type"] == "project":
            webhooks.set_project_webhook(item["gid"], domain, asana)
            print("Setting new webhook for ", item["name"])

    print("New webhooks set. Complete!")
    return
