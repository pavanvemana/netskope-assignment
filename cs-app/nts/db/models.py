from datetime import datetime, UTC, timedelta
import traceback

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.engine import Session

from .constants import EscalationLevels, TicketStates, SLAClock, SLAStates


Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(String, primary_key=True)
    priority = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    customer_tier = Column(String, nullable=False)
    status = Column(String, nullable=False)
    status_history = relationship("TicketStatusHistory", backref="ticket", cascade="all, delete-orphan")
    sla_clocks = relationship("SLA", backref="ticket", cascade="all, delete-orphan")
    escalation_level = Column(Integer, nullable=False, default=EscalationLevels.LEVEL_1.value)

    # Maintain idempotency to avoid duplicate updates
    __table_args__ = (
        UniqueConstraint('id', 'updated_at', name='ticket_id_updated_unique'),
    )

    def __repr__(self):
        return f"<Ticket(id=NTSK-{self.id}, priority='{self.priority}', tier='{self.customer_tier}')>"
    
    @classmethod
    def create(cls, kwargs):
        try:
            with Session() as session:
                # Creating a Ticket
                ticket = cls(**kwargs)
                session.add(ticket)
                session.commit()
        except sqlalchemy.exc.IntegrityError:
            print('Duplicate request/record')
        except Exception as error:
            print('An uknown error occured while creating ticket')
            print(traceback.format_exc())
    
    @classmethod
    def update(cls, kwargs):
        try:
            with Session() as session:
                # Updating a Ticket
                ticket = session.get(cls, {'id': kwargs.get('id')})
                if ticket:
                    for key, value in kwargs.items():
                        if key != 'id':
                            setattr(ticket, key, value)
                    session.commit()
                    return True
                return False
        except sqlalchemy.exc.IntegrityError:
            print('Duplicate request/record')
        except Exception as error:
            print('An uknown error occured while updating ticket')
            print(traceback.format_exc())
    
    def get_info(self):
        resp = {}
        with Session() as session:
            sla = session.query(SLA).join(Ticket).filter(
                    SLA.sla_type == SLAClock.RESOLUTION.value,
                    SLA.ticket_id == self.id
                ).first()
            resp['ticket_id'] = self.id
            resp['sla_status'] = sla.status
            resp['remaining_time'] = sla.get_remaining_time()
            resp['escalation_leve'] = self.escalation_level
        return resp



class TicketStatusHistory(Base):
    __tablename__ = 'ticket_status_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey('ticket.id'), nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False, default=TicketStates.OPEN.value)
    changed_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    changed_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<TicketStatusHistory(ticket_id={self.ticket_id}, from='{self.old_status}', to='{self.new_status}', at='{self.changed_at}')>"


class SLA(Base):
    __tablename__ = 'ticket_sla'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey('ticket.id'), nullable=False)
    sla_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    sla_start_time =  Column(DateTime(timezone=True), default=datetime.now(UTC))
    sla_target_time = Column(DateTime(timezone=True))
    status = Column(String, nullable=False)
    sla_history = relationship(
        "SLAHistory", 
        backref="ticket_sla", 
        cascade="all, delete-orphan"
    )
    

    def __repr__(self):
        return f"<TicketStatusHistory(ticket_id={self.ticket_id}, type='{self.sla_type}', from='{self.sla_start_time}', to='{self.sla_target_time}')>"
    
    # Maintain idempotency to avoid duplicate updates
    __table_args__ = (
        UniqueConstraint('id', 'updated_at', name='sla_id_updated_unique'),
    )

    def get_total_paused_time(self):
        total_paused_time = timedelta(0)
        paused_start = None

        sla_history = sorted(self.sla_history, key=lambda x: x.changed_at)

        for history in sla_history:
            if history.new_status == SLAStates.PAUSED and not paused_start:
                paused_start = history.changed_at
            elif paused_start and history.new_status != SLAStates.PAUSED:
                total_paused_time += history.changed_at - paused_start
                # Reset start time of PAUSED state
                paused_start = None
        
        if paused_start:
            total_paused_time += datetime.now(UTC) - paused_start
        print(total_paused_time)
        return total_paused_time
    

    def get_remaining_time(self):
        active_time = datetime.now(UTC) - self.sla_start_time - self.get_total_paused_time()
        remaining_time = self.sla_target_time - (self.sla_start_time + active_time)
        if remaining_time.total_seconds() < 0:
            return timedelta(0)
        return f'{round(remaining_time.total_seconds()/60, 1)} Minutes'


class SLAHistory(Base):
    __tablename__ = 'ticket_sla_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sla_id = Column(Integer, ForeignKey('ticket_sla.id'), nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    changed_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<TicketStatusHistory(sla_id={self.sla_id}, from='{self.old_status}', to='{self.new_status}', at='{self.changed_at}')>"

