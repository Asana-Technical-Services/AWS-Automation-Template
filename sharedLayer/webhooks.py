"""
sharedLater/webhooks.py
A set of functions to manage Asana webhooks
"""
import urllib.parse
import os
import requests
import json
import asana_client

# Deletes all active webhooks in the workspace
def delete_active_webhooks(asana):
    workspace_gid = os.environ["WORKSPACE_GID"]
    url = f"webhooks?&workspace={workspace_gid}"

    response = asana.request("GET", url)

    if not response["success"]:
        print("get webhooks on resource request failed")
        return False

    active_webhooks = response["data"]

    # delete webhooks
    for hook in active_webhooks:
        hook_success = remove_webhook(hook["gid"], asana)
        if not hook_success:
            print("did not delete webhook: ", hook)

    return True

# Deletes an existing webhook
def remove_webhook(webhook_gid, asana):
    url = f"webhooks/{webhook_gid}"

    response = asana.request("DELETE", url)

    return response["success"]

# Establishes a webhook for a Portfolio: projects added or removed
def set_portfolio_webhook(portfolio_gid, domain, asana):

    url = "webhooks"
    data = {
        "data": {
            "filters": [
                {"action": "added", "resource_type": "project"},
                {"action": "removed", "resource_type": "project"},
            ],
            "resource": portfolio_gid,
            "target": f"{domain}/bot?webhook_resource=portfolio&resource_gid={portfolio_gid}",
        }
    }

    response = asana.request("POST", url, data)

    return response["success"]

# Establishes a webhook for a Project: tasks added
def set_project_webhook_new_tasks(project_gid, domain, asana):
    url = "webhooks"
    data = {
        "data": {
            "filters": [
                {
                    "action": "added",
                    "resource_type": "task"
                }
            ],
            "resource": project_gid,
            "target": f"{domain}/bot?webhook_resource=project&resource_gid={project_gid}",
        }
    }

    response = asana.request("POST", url, data)

    return response["success"]

# Establishes a webhook for a Project: tasks' custom fields updated
def set_project_webhook_task_custom_fields_updated(project_gid, domain, asana):
    url = "webhooks"
    data = {
        "data": {
            "filters": [
                {
                    "action": "changed",
                    "fields": [
                        "custom_fields",
                    ],
                    "resource_type": "task",
                }
            ],
            "resource": project_gid,
            "target": f"{domain}/bot?webhook_resource=project&resource_gid={project_gid}",
        }
    }

    response = asana.request("POST", url, data)

    return response["success"]