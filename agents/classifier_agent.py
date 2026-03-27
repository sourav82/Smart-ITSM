from vertexai.generative_models import GenerativeModel
from utils.vertex_client import *

model = GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You classify IT incidents into queues:

Return one of:
Network-L2 - This is related to any network connectivity issues, like connecting to Internet, on-premise to Cloud etc.
MBS-L2 - MBS is Major Business Services which includes application like EAP, Intellipay, Cloudapp, MajorTrails, Mobility. Any issues, other than connectivity, in these applications will be assigned to MBS-L2
IBS-L2 - IBS stands for Important Business Services which includes application like ALPS, DAST, SASM, APPIM. Any issues with these applications, other than network connectivity, will be assigned to this queue IBS-L2
Algo-L2 - This queue delas with any application issues other than network connectivity for Algo applications.

You need to only provide the most likely name of the group (from Network-L2, MBS-L2, IBS-L2, Algo-L2). 

If none of the above groups are matching with the incident description, the always return the group "Level-1". Service has this group as well.
Level-1 is the default group if the assignment group cannot be established from the above groups.

Again, only return the group name from Network-L2, MBS-L2, IBS-L2, Algo-L2, Level-1

"""

def classify(description: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\nIncident:\n{description}"
    response = model.generate_content(prompt)
    return response.text.strip()