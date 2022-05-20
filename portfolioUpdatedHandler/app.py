"""
potfolioUpdatedHandler/app.py
Lambda Function that manages the addition and removal of projects in a portfolio
"""
import secrets
import os
import json
import urllib
import webhooks
from asana_client import Asana_Client


def lambda_handler(message, context):
    print(message)
    project_id = message["projectId"]
    if project_id is None:
        print("no project id")
        return

    change = message["change"]

    if change != "added" and change != "removed":
        return

    domain = f'https://{message["domain"]}/Prod'

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

    if change == "added":
        # add new webhook
        webhooks.set_project_webhook(project_id, domain, asana)

    elif change == "removed":
        # get all webhooks for that resource
        url = f'webhooks?resource={project_id}&workspace={os.environ["WORKSPACE_GID"]}'

        response = asana.request("GET", url)

        if not response["success"]:
            print("get webhooks on resource request failed")
            return

        active_webhooks = response["data"]

        # delete webhooks
        for hook in active_webhooks:
            webhooks.remove_webhook(hook["gid"], asana)

    return
