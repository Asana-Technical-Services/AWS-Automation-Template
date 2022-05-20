"""
taskEventHandler/app.py
Lambda Function that performs a certain set of actions after a task event
"""
from traceback import print_tb
import os
import secrets
from asana_client import Asana_Client

def lambda_handler(message, context):
    print(message)

    task_gid = message["taskGid"]
    project_gid = message["projectGid"]
    # user_gid = message["userGid"]

    if task_gid is None:
        print("empty task ID")
        return

    bot_secret_arn = os.environ["BOT_SECRET_ARN"]
    try:
        bot_secrets = secrets.get_secret_value(bot_secret_arn)
        api_key = bot_secrets["API_KEY"]
    except:
        print(
            "Could not access Asana secret keys. Check that they are set in Secrets Manager"
        )
        return

    asana = Asana_Client(api_key)
    
    # Retrieve task
    task = None

    url = f"tasks/{task_gid}?opt_fields=notes"
    result = asana.request("GET", url)

    if not result["success"]:
        print("Task request failed, exiting")
        return

    task = result["data"]
    
    print(task)
    
    # Perform the desired actions with the task
    # ...
    
    # Return
    return
