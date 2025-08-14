from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, SmallInteger, UniqueConstraint, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import  relationship
from sqlalchemy.sql import text
from app.core.postgres.db_engine import Base


class Device(Base):
    __tablename__ = "devices"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    brand = Column(String(64), nullable=False, index=True)
    type = Column(String(32), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    __table_args__ = (UniqueConstraint('brand', 'type', 'name', name='uq_device_brand_type_name'),)

class Model(Base):
    __tablename__ = "models"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(128), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    device = relationship("Device")
    __table_args__ = (UniqueConstraint('device_id', 'name', name='uq_model_device_name'),)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    slug = Column(String(64), nullable=False, unique=True)
    title = Column(String(128), nullable=False)
    onsite_default = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

class PriceRule(Base):
    __tablename__ = "price_rules"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='SET NULL'))
    model_id = Column(UUID(as_uuid=True), ForeignKey('models.id', ondelete='SET NULL'))
    issue_id = Column(UUID(as_uuid=True), ForeignKey('issues.id', ondelete='SET NULL'))
    base_price = Column(Numeric(12,2))
    min_price = Column(Numeric(12,2))
    max_price = Column(Numeric(12,2))
    currency = Column(String(3), nullable=False, server_default='KZT')
    eta_min = Column(SmallInteger())
    eta_max = Column(SmallInteger())
    warranty_months = Column(SmallInteger())
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    __table_args__ = (Index('ix_price_rules_triplet', 'device_id', 'model_id', 'issue_id', unique=True),)

class Zone(Base):
    __tablename__ = "zones"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(64), nullable=False, unique=True)
    geo = Column(JSONB)
    extra_fee = Column(Numeric(12,2), server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)