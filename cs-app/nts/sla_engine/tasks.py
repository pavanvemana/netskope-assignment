import os
import logging
from datetime import datetime, UTC

from celery import Celery
from db.engine import Session
from celery.schedules import crontab
from sqlalchemy.exc import SQLAlchemyError

from db.models import SLA, Ticket, SLAAlert
from db.constants import TicketStates, SLAStates
from utils.slack import post_message

log = logging.getLogger(__name__)

app = Celery('sla_alerts')
app.conf.broker_url = 'redis://redis:6379/0'

@app.task
def process_sla_alerts():
    with Session() as session:
        tickets = session.query(Ticket).filter(Ticket.status==TicketStates.OPEN).all()
        for ticket in tickets:
            for sla_clock in ticket.sla_clocks:
                sla_start = sla_clock.sla_start_time
                active_time = (datetime.now(UTC) - sla_start - sla_clock.get_total_paused_time()).seconds // 60
                total_time = (sla_clock.sla_target_time - sla_clock.sla_start_time).seconds // 60
                log.info('Active time - %s, Total time - %s', active_time, total_time)
                perc_time_remaining = ((total_time - active_time)/total_time) * 100
                log.info('Remainig time - %s', perc_time_remaining)
                if 1 <= perc_time_remaining <= 15:
                    log.info('%s Remaining SLA <= 15 percent - %s. Alert raised.', sla_clock.sla_type, sla_clock.ticket_id)
                    if not sla_clock.sla_alerts:
                        try:
                            alert = SLAAlert(sla_id=sla_clock.id, alert_type=sla_clock.sla_type)
                            session.add(alert)
                            session.commit()
                        except SQLAlchemyError as error:
                            log.error('An error occured while creating records in DB - %s', error)
                            session.rollback()
                    else:
                        log.info('Alert already raised for ticket - %s', sla_clock.ticket_id)
                elif perc_time_remaining < 1:
                    log.info('SLA breached for ticket - %s', sla_clock.ticket_id)
                    if not sla_clock.sla_alerts:
                        try:
                            alert = SLAAlert(sla_id=sla_clock.id, alert_type=sla_clock.sla_type)
                            session.add(alert)
                            sla_clock.ticket.escalation_level =  sla_clock.ticket.escalation_level + 1
                            sla_clock.status = SLAStates.BREACHED
                            session.add(sla_clock)
                            session.commit()
                        except SQLAlchemyError as error:
                            log.error('An error occured while creating records in DB - %s', error)
                        # Send message to slack web hook
                        post_message(f'{sla_clock.sla_type} SLA breached for ticket - {sla_clock.ticket_id}')
                    else:
                         log.info('Alert already raised for ticket - %s', sla_clock.ticket_id)
                   
            


app.conf.beat_schedule = {
    'sla-process-5mins': {
        'task': 'sla_engine.tasks.process_sla_alerts',
        'schedule': crontab(minute='*'),
    },
}
app.conf.timezone = 'UTC'