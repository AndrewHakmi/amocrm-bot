from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import text

from app.core.postgres.db_engine import Base

class Master(Base):
    __tablename__ = "masters"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(128), nullable=False)
    phone = Column(String(32), index=True)
    calendar_external_id = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

class MasterSkill(Base):
    __tablename__ = "master_skills"
    master_id = Column(UUID(as_uuid=True), ForeignKey('masters.id', ondelete='CASCADE'), primary_key=True)
    issue_id = Column(UUID(as_uuid=True), ForeignKey('issues.id', ondelete='CASCADE'), primary_key=True)

class MasterZone(Base):
    __tablename__ = "master_zones"
    master_id = Column(UUID(as_uuid=True), ForeignKey('masters.id', ondelete='CASCADE'), primary_key=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey('zones.id', ondelete='CASCADE'), primary_key=True)

class Availability(Base):
    __tablename__ = "availability"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    master_id = Column(UUID(as_uuid=True), ForeignKey('masters.id', ondelete='CASCADE'), nullable=False)
    start = Column(DateTime(timezone=True), nullable=False, index=True)
    end = Column(DateTime(timezone=True), nullable=False, index=True)
    is_booked = Column(Boolean, nullable=False, server_default=text('false'))
    __table_args__ = (UniqueConstraint('master_id','start','end', name='uq_availability_slot'),)

class LeadLink(Base):
    __tablename__ = "lead_links"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    amo_lead_id = Column(String, unique=True)
    amo_contact_id = Column(String)
    phone = Column(String(32), index=True)
    source_channel = Column(String(32), nullable=False, server_default='other')
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    master_id = Column(UUID(as_uuid=True), ForeignKey('masters.id', ondelete='RESTRICT'), nullable=False)
    lead_link_id = Column(UUID(as_uuid=True), ForeignKey('lead_links.id', ondelete='SET NULL'))
    status = Column(String(32), nullable=False, server_default='PENDING')
    start = Column(DateTime(timezone=True), nullable=False, index=True)
    end = Column(DateTime(timezone=True), nullable=False, index=True)
    address = Column(String(256))
    lat = Column(Numeric(10,7))
    lng = Column(Numeric(10,7))
    zone_id = Column(UUID(as_uuid=True), ForeignKey('zones.id', ondelete='SET NULL'))
    calendar_event_id = Column(String(256))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    ts = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False, index=True)
    kind = Column(String(64), nullable=False, index=True)
    payload = Column(JSONB)