import requests
from app.config import settings

import requests
from requests.auth import HTTPBasicAuth
import logging
import random

def get_queue_sys_id(queue_name):

    url = f"{settings.SERVICENOW_INSTANCE}/api/now/table/sys_user_group"

    params = {
        "sysparm_query": f"name={queue_name}",
        "sysparm_fields": "sys_id,name"
    }

    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD),
        headers={"Accept": "application/json"},
        params=params
    )

    data = response.json()

    if data["result"]:
        return data["result"][0]["sys_id"]

    return None

def get_group_members(group_sys_id):
    print(f"Group sys id: {group_sys_id}")
    url = f"{settings.SERVICENOW_INSTANCE}/api/now/table/sys_user_grmember"
    params = {
        "sysparm_query": f"group={group_sys_id}",
        "sysparm_fields": "user"
    } 
    headers = {
        "Accept": "application/json"
    }           
    r = requests.get(url, auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD), params=params, headers=headers)
    print("Status:", r.status_code)
    print("Response:", r.text)
    if r.status_code != 200:
        logging.error(f"Failed to fetch group members: {r.status_code} {r.text}")
        return []
    try:
        data = r.json()
    except Exception as e:
        logging.error(f"Invalid JSON response: {r.text}")
        return []
    print(f"Data: {data}")
    members = []
    print(f"Value of R: {r}")
    for item in data.get("result", []):
        user_field = item.get("user")
        if isinstance(user_field, dict) and "value" in user_field:
            members.append(user_field["value"])
    logging.info(f"Found {len(members)} members in group {group_sys_id}")
    return members


def update_incident(sys_id, incident_id, queue, comment="", state=None):

    url = f"{settings.SERVICENOW_INSTANCE}/api/now/table/incident/{sys_id}"

    queue_sys_id = get_queue_sys_id(queue)
    # Fetch team members
    members = get_group_members(queue_sys_id)
    if not members:
        logging.warning(f"No members found in group {queue_sys_id}. Assigning to None.")
        assigned_to = None
    else:
        assigned_to = random.choice(members)
    assigned_to = random.choice(members) if members else None
    payload = {}

    if queue_sys_id:
        payload["assignment_group"] = queue_sys_id

    if assigned_to:
        payload["assigned_to"] = assigned_to

    if comment:
        payload["comments"] = comment

    if state:
        payload["state"] = state


    response = requests.patch(
        url,
        auth=(settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD),
        json=payload
    )

    return response.json()