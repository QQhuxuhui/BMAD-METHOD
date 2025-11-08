"""add_user_and_model_config_tables

Revision ID: 0b645592c28d
Revises: 7eb39e955576
Create Date: 2025-11-07 10:58:27.807350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b645592c28d'
down_revision: Union[str, None] = '7eb39e955576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create model_configs table
    op.create_table(
        'model_configs',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('api_base_url', sa.String(length=500), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='4096'),
        sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('api_key_encrypted', sa.String(length=500), nullable=True),
        sa.Column('timeout', sa.Float(), nullable=False, server_default='30.0'),
        sa.Column('extra_params', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for model_configs
    op.create_index(op.f('ix_model_configs_name'), 'model_configs', ['name'], unique=True)
    op.create_index(op.f('ix_model_configs_provider'), 'model_configs', ['provider'], unique=False)
    op.create_index(op.f('ix_model_configs_is_active'), 'model_configs', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_model_configs_is_active'), table_name='model_configs')
    op.drop_index(op.f('ix_model_configs_provider'), table_name='model_configs')
    op.drop_index(op.f('ix_model_configs_name'), table_name='model_configs')

    # Drop table
    op.drop_table('model_configs')
