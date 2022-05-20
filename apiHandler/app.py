"""
apiHandler/app.py
Lambda Function that reviews the events received from Asana and routes
to the appropriate workflow
"""
import os
import json
import boto3
import secrets

def lambda_handler(event, context):

    # Init
    secret = None
    signature = None
    event_headers = event["headers"]
    bot_state_machine_arn = os.environ["BOT_STATE_MACHINE_ARN"]
    state_machine_client = boto3.client("stepfunctions")

    try:
        event_webhook_resource = event["queryStringParameters"]["webhook_resource"]
        event_resource_gid = event["queryStringParameters"]["resource_gid"]
    except:
        print("incoming event did not include action and resource_gid query parameters")
        return

    # Retrieve secret or signature
    try:
        secret = event_headers["X-Hook-Secret"]
    except:
        print("x-hook-secret does not exist")

    try:
        signature = event_headers["X-Hook-Signature"]
    except:
        print("x-hook-signature does not exist")

    bot_secrets = secrets.get_secret_value(os.environ["BOT_SECRET_ARN"])

    if secret is not None:
        # New webhook connection
        print("secret is not None")

        # set the webhook secret for that resource's webhook
        bot_secrets[event_resource_gid] = secret
        print("updated")
        secrets.update_secret(os.environ["BOT_SECRET_ARN"], json.dumps(bot_secrets))

        # Callback OK with secret
        return {
            "statusCode": 200,
            "headers": {"X-Hook-Secret": secret},
            "body": json.dumps({}),
        }

    elif signature is not None:
        # New webhook events

        # Validate signature
        if (event_resource_gid in bot_secrets) and (
            secrets.verify_signature(
                signature, bot_secrets[event_resource_gid], event["body"]
            )
        ):

            # Iterate through events
            event_body = json.loads(event["body"])
            asana_events = event_body["events"]

            # In case of duplicate events, keep track of tasks we've seen.
            triggered_tasks = {}
            
            print(event_webhook_resource)
            print(event_resource_gid)

            for asana_event in asana_events:

                # Retrieve event information
                action = asana_event["action"]
                resource = asana_event["resource"]
                user = asana_event["user"]

                print(asana_event)

                # Validate event = new task has been added to a project
                if (
                    event_webhook_resource == "project"
                    and action == "added"
                    and resource["resource_type"] == "task"
                    and resource["gid"] not in triggered_tasks
                ):
                    # Tasks coming from a form submission
                    if user is None:
                        input = json.dumps(
                            {
                                "action": "NEW_TASK_FROM_FORM",
                                "taskGid": resource["gid"],
                                "projectGid": event_resource_gid
                            }
                        )
                        
                        print("Execute automation for new task from form")
                        state_machine_client.start_execution(
                            stateMachineArn=bot_state_machine_arn, input=input
                        )

                        triggered_tasks[resource["gid"]] = True
                    
                    # Tasks created by an user
                    else:
                        input = json.dumps(
                            {
                                "action": "NEW_TASK_FROM_USER",
                                "taskGid": resource["gid"],
                                "projectGid": event_resource_gid,
                                "userGid": asana_event["user"]["gid"],
                            }
                        )
                        
                        print("Execute automation for new task from user")
                        state_machine_client.start_execution(
                            stateMachineArn=bot_state_machine_arn, input=input
                        )

                        triggered_tasks[resource["gid"]] = True
                        
                # Validate event = task custom fields updated
                # you can filter by specific custom fields with:
                # """
                # and asana_event["change"]["field"] == "custom_fields"
                # and asana_event["change"]["new_value"]["gid"]
                # == os.environ["CF_GID"]                
                # """
                elif (
                    event_webhook_resource == "project"
                    and action == "changed"
                    and resource["gid"] not in triggered_tasks
                ):
                    input = json.dumps(
                        {
                            "action": "TASK_UPDATED",
                            "taskGid": resource["gid"],
                            "projectGid": event_resource_gid,
                            "userGid": asana_event["user"]["gid"],
                        }
                    )
                    
                    print("Execute automation for task updated")
                    state_machine_client.start_execution(
                        stateMachineArn=bot_state_machine_arn, input=input
                    )

                    triggered_tasks[resource["gid"]] = True
                        
                # Validate event = project was added or removed in a portfolio
                elif event_webhook_resource == "portfolio" and (
                    action == "added" or action == "removed"
                ):
                    domainName = event["requestContext"]["domainName"]
                    input = json.dumps(
                        {
                            "action": "PORTFOLIO_PROJECTS_UPDATED",
                            "projectId": resource["gid"],
                            "domain": domainName,
                            "change": action,
                        }
                    )

                    print("Execute automation for project update in a portfolio")
                    state_machine_client.start_execution(
                        stateMachineArn=bot_state_machine_arn, input=input
                    )

                # Discard
                else:
                    print("Event discarded")

            # Callback OK
            return {"statusCode": 200, "body": json.dumps({})}
        else:
            # Callback 401 unauthorized
            return {"statusCode": 401, "body": json.dumps({})}

    else:
        # Callback 401 unauthorized
        return {"statusCode": 401, "body": json.dumps({})}
