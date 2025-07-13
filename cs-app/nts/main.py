from typing import Union

from fastapi import FastAPI
from api import tickets
from db.engine import Session
from db.models import Ticket, SLA
from sla_engine.tasks import process_sla_alerts

app = FastAPI()

app.include_router(tickets.router)

@app.on_event("startup")
def on_startup():
    from db.models import Base
    from db.engine import engine
    Base.metadata.create_all(engine)


@app.get('/dashboard')
async def dashboard(limit: str, offset: str, sla_state: str = None,):
    resp = []
    with Session() as session:
        tickets = session.query(Ticket).join(Ticket.sla_clocks)
        if sla_state:
            tickets = tickets.filter(SLA.status == sla_state)
        if limit and offset:
            tickets = tickets.offset(offset).limit(limit)
        else:
            tickets = tickets.all()
        for ticket in tickets:
            resp.append(ticket.get_info())
    return resp

@app.get('/process_alerts')
async def process_alerts():
    process_sla_alerts.delay()
    return 'Task queued'