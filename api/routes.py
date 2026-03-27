from fastapi import APIRouter
from workflows.incident_workflow import process_incident
from workflows.resolution_workflow import process_resolution

router = APIRouter()

@router.post("/incident")
async def incident(payload: dict):

    return await process_incident(payload)


@router.post("/incident/resolved")
async def resolved(payload: dict):

    return await process_resolution(payload)