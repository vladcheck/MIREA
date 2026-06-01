from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '125369597064'
down_revision: Union[str, Sequence[str], None] = '21d7364fdb79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('products', sa.Column('description', sa.String(), server_default='No description', nullable=False))

def downgrade() -> None:
    op.drop_column('products', 'description')
