from agents.classifier_agent import classify
from agents.kb_retrieval_agent import search_kb
from services.servicenow_service import update_incident
from services.email_service import send_email
from services.servicenow_service import get_queue_sys_id, get_group_members

async def process_incident(payload):

    description = payload["description"]
    incident_id = payload["number"]
    sys_id = payload["sys_id"]

    queue = classify(description)

    kb_articles = search_kb(description)

    if kb_articles:
        comment = "Relevant KB:\n" + "\n".join(kb_articles)
        update_incident(sys_id, incident_id, queue, comment, state="2")
    else:
        update_incident(sys_id, incident_id=incident_id, queue=queue, state="2")
        queue_sys_id = get_queue_sys_id(queue)
        members = get_group_members(queue_sys_id)
        send_email(members, incident_id, description)

    return {"status": "processed"}