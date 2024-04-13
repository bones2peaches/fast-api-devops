"""empty message

Revision ID: b09331f2d343
Revises: 2fd8ec6fa093, a89bb1ddc47f
Create Date: 2024-03-30 20:12:33.501100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b09331f2d343'
down_revision: Union[str, None] = ('2fd8ec6fa093', 'a89bb1ddc47f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
