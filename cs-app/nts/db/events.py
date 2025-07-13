from datetime import datetime, UTC, timedelta

from sqlalchemy import event, inspect
from sqlalchemy.orm import object_session
from sqlalchemy.orm.attributes import set_committed_value
from db.engine import Session

from .models import Ticket, TicketStatusHistory, SLA, SLAHistory
from .constants import SLAStates, SLAClock, TicketStates
from utils import get_sla_targets

@event.listens_for(Ticket, 'before_update')
def ticket_before_update(mapper, connection, target):
    '''
    Event listener for ticket to record state changes in session
    '''
    session = object_session(target)
    if not session:
        return
    set_committed_value(target, 'updated_at', datetime.now(UTC))
    state = inspect(target)
    if state.attrs.status.history.has_changes():
        old_status = state.attrs.status.history.deleted[0] if state.attrs.status.history.deleted else None
        new_status = target.status
        changes = session.info.setdefault('ticket_status_changes', {})
        changes.update({'ticket_id': target.id, 'old': old_status, 'new': new_status})


@event.listens_for(Session, 'after_commit')
def after_commit(session):
        '''
        Event listener which is trigger after commit.
        Function gets ticket status changes from session and updates 
        ticket status hisotry and SLA states
        '''
        ticket_status_changes = session.info.pop('ticket_status_changes', {})
        if ticket_status_changes:
            old_status = ticket_status_changes.get('old')
            new_status = ticket_status_changes.get('new')
            ticket_id = ticket_status_changes.get('ticket_id')
            with Session() as curr_session:
                if old_status != new_status:
                    curr_session.add(
                        TicketStatusHistory(
                            ticket_id = ticket_id,
                            new_status = new_status,
                            old_status = old_status,
                            changed_at = datetime.now(UTC)
                        )
                    )
                if old_status ==  TicketStates.OPEN.value and new_status == TicketStates.IN_PROGRESS.value:
                    sla = curr_session.query(SLA).filter_by(ticket_id=ticket_id, sla_type=SLAClock.RESPONSE.value).first()
                    sla.status = SLAStates.STOPPED.value
                elif old_status != new_status and new_status == TicketStates.AWAITING_CUSTOMER.value:
                    sla = curr_session.query(SLA).filter_by(ticket_id=ticket_id, sla_type=SLAClock.RESOLUTION.value).first()
                    sla.status = SLAStates.PAUSED.value
                elif new_status == TicketStates.RESOLVED:
                    sla = curr_session.query(SLA).filter_by(ticket_id=ticket_id, sla_type=SLAClock.RESOLUTION.value).first()
                    sla.status =  SLAStates.STOPPED.value
                elif new_status == TicketStates.IN_PROGRESS and old_status == TicketStates.AWAITING_CUSTOMER:
                    sla = curr_session.query(SLA).filter_by(ticket_id=ticket_id, sla_type=SLAClock.RESOLUTION.value).first()
                    sla.status =  SLAStates.ACTIVE.value
                curr_session.commit()



@event.listens_for(Ticket, 'after_insert')
def after_ticket_creation(mapper, connection, target):
    @event.listens_for(Session, 'after_flush', once=True)
    def after_flush(session, context):
        '''
        Event listener to create Response and Resolution SLAs
        based on pre-configured targets in sla_config.yaml
        '''
        # Create SLAs for ticket
        sla_targets = get_sla_targets(target.customer_tier, target.priority)
        # Creating SLA for response
        response_sla = SLA(
            ticket_id = target.id,
            status = SLAStates.ACTIVE.value,
            sla_type = SLAClock.RESPONSE.value,
            sla_target_time = datetime.now(UTC) + timedelta(minutes=sla_targets.get('response')),
        )
        session.add(response_sla)
        # Creating SLA for resolution
        resolution_sla = SLA(
            ticket_id = target.id,
            status = SLAStates.ACTIVE.value,
            sla_type = SLAClock.RESOLUTION.value,
            sla_target_time = datetime.now(UTC) + timedelta(minutes=sla_targets.get('resolution')),
        )
        session.add(resolution_sla)


@event.listens_for(SLA, 'before_update')
def sla_before_update(mapper, connection, target):
    '''
    Event listener to record SLA state change history
    '''
    session = object_session(target)
    if not session:
        return
    state = inspect(target)
    set_committed_value(target, 'updated_at', datetime.now(UTC))
    # Check status changes
    if state.attrs.status.history.has_changes():
        old_status = state.attrs.status.history.deleted[0] if state.attrs.status.history.deleted else None
        new_status = state.attrs.status.history.added[0] if state.attrs.status.history.added else None
        if old_status != new_status:
            session.add(
                SLAHistory(
                    sla_id = target.id,
                    new_status = new_status,
                    old_status = old_status,
                    changed_at = datetime.now(UTC)
                )
            )
