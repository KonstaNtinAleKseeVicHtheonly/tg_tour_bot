"""изменил стобец price_per_person  в Туре на строку так проще

Revision ID: d8ffe5df442d
Revises: b092de091a59
Create Date: 2026-01-02 18:24:23.894675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8ffe5df442d'
down_revision: Union[str, Sequence[str], None] = 'b092de091a59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Удаляем старый столбец (данные потеряются!)
    op.drop_column('tours', 'price_per_person')
    
    # 2. Создаем новый
    op.add_column('tours', sa.Column('price_per_person', 
                                     sa.String(length=20), 
                                     nullable=False,
                                     comment='Цена за человека в рублях'))

def downgrade() -> None:
    # 1. Удаляем строковый
    op.drop_column('tours', 'price_per_person')
    
    # 2. Создаем numeric обратно
    op.add_column('tours', sa.Column('price_per_person',
                                     sa.NUMERIC(precision=10, scale=2),
                                     nullable=False,
                                     comment='Цена за человека в рублях'))