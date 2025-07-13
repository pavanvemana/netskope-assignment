from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from db.engine import Session
from db.models import Ticket, SLA
import db.events


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get('/{ticket_id}')
async def get_tickets(ticket_id):
    with Session() as session:
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return JSONResponse(
                {'message': 'Ticket not found'},
                status_code=404
            )
        else:
            return JSONResponse(
                ticket.get_info()
            )

@router.post('/')
async def create_tickets(request: Request):
    tickets = await request.json()
    for ticket in tickets:
        Ticket.create(ticket)
    return JSONResponse({'message': 'created'}, status_code=201)


@router.put('/')
async def update_tickets(request: Request):
    tickets = await request.json()
    resp = {}
    for ticket in tickets:
        update_status = Ticket.update(ticket)
        resp[ticket['id']] = update_status
    return resp

