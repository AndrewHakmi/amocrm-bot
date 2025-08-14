from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('brand', sa.String(64), nullable=False, index=True),
        sa.Column('type', sa.String(32), nullable=False, index=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('brand', 'type', 'name', name='uq_device_brand_type_name')
    )

    op.create_table(
        'models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(128), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('device_id', 'name', name='uq_model_device_name')
    )

    op.create_table(
        'issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('slug', sa.String(64), nullable=False, unique=True),
        sa.Column('title', sa.String(128), nullable=False),
        sa.Column('onsite_default', sa.Boolean(), nullable=False,
                  server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False)
    )

    op.create_table(
        'price_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('issue_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('base_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('min_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('max_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='KZT'),
        sa.Column('eta_min', sa.SmallInteger(), nullable=True),
        sa.Column('eta_max', sa.SmallInteger(), nullable=True),
        sa.Column('warranty_months', sa.SmallInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='SET NULL'),
        sa.Index('ix_price_rules_triplet', 'device_id', 'model_id', 'issue_id', unique=True)
    )

    op.create_table(
        'zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(64), nullable=False, unique=True),
        sa.Column('geo', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('extra_fee', sa.Numeric(12, 2), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False)
    )

    # --- Masters and skills/zones ---
    op.create_table(
        'masters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('phone', sa.String(32), nullable=True, index=True),
        sa.Column('calendar_external_id', sa.String(256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False)
    )

    op.create_table(
        'master_skills',
        sa.Column('master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['master_id'], ['masters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('master_id', 'issue_id', name='pk_master_skills')
    )

    op.create_table(
        'master_zones',
        sa.Column('master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['master_id'], ['masters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('master_id', 'zone_id', name='pk_master_zones')
    )

    op.create_table(
        'availability',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('end', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('is_booked', sa.Boolean(), nullable=False,
                  server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['master_id'], ['masters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('master_id', 'start', 'end', name='uq_availability_slot')
    )


    op.create_table(
        'lead_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('amo_lead_id', sa.BigInteger(), nullable=True, unique=True),
        sa.Column('amo_contact_id', sa.BigInteger(), nullable=True),
        sa.Column('phone', sa.String(32), nullable=True, index=True),
        sa.Column('source_channel', sa.String(32), nullable=False, server_default='other'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lead_link_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='PENDING'),
        sa.Column('start', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('end', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('address', sa.String(256), nullable=True),
        sa.Column('lat', sa.Numeric(10, 7), nullable=True),
        sa.Column('lng', sa.Numeric(10, 7), nullable=True),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('calendar_event_id', sa.String(256), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['master_id'], ['masters.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['lead_link_id'], ['lead_links.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ondelete='SET NULL')
    )

    op.create_table(
        'event_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('ts', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('kind', sa.String(64), nullable=False, index=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Index('ix_event_logs_ts', 'ts')
    )

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade():
    op.drop_index('ix_event_logs_ts', table_name='event_logs')
    op.drop_table('event_logs')
    op.drop_table('bookings')
    op.drop_table('lead_links')
    op.drop_table('availability')
    op.drop_table('master_zones')
    op.drop_table('master_skills')
    op.drop_table('masters')
    op.drop_table('zones')
    op.drop_index('ix_price_rules_triplet', table_name='price_rules')
    op.drop_table('price_rules')
    op.drop_table('issues')
    op.drop_table('models')
    op.drop_table('devices')
    op.drop_table('users')