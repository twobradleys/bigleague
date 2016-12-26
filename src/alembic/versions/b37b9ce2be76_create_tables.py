"""Create the tables."""
from alembic import op
from sqlalchemy.sql import column

from bigleague.lib.sports import GAME_STATES

# revision identifiers, used by Alembic.
revision = 'b37b9ce2be76'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade."""
    create_team_table()
    create_game_table()
    create_player_table()
    create_cell_table()


def create_team_table():
    op.execute("""
        CREATE TABLE team (
            id UUID NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            name VARCHAR(256) NOT NULL,
            sport VARCHAR(64) NOT NULL
        )""")  # noqa
    op.create_primary_key("pk_team", "team", ["id"])
    op.create_unique_constraint("uq_name_sport", "team", ["name", "sport"])


def create_game_table():
    op.execute("""
        CREATE TABLE game (
            id UUID NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            event_name VARCHAR(256) NOT NULL,
            event_description VARCHAR(256),
            sport VARCHAR(64) NOT NULL,
            history JSON NOT NULL,
            state VARCHAR(32),
            home_team_id VARCHAR(64) NOT NULL,
            away_team_id VARCHAR(64) NOT NULL,
            home_score INT NOT NULL,
            away_score INT NOT NULL
        )""")  # noqa

    op.create_check_constraint(
        "ck_game_state",
        "game",
        column('state').in_(GAME_STATES)
        & (column('home_team_id') != column('away_team_id')))

    op.create_primary_key("pk_game", "game", ["id", "timestamp"])


def create_player_table():
    op.execute("""
        CREATE TABLE player (
            id UUID NOT NULL,
            handle VARCHAR(64) NOT NULL,
            auth_token UUID
        )
        """)  # noqa

    op.create_primary_key("pk_player", "player", ["id"])
    op.create_unique_constraint("uq_player", "player", ["handle"])


def create_cell_table():
    op.execute("""
        CREATE TABLE cell (
            game_id UUID NOT NULL,
            home_index SMALLINT NOT NULL,
            away_index SMALLINT NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            home_digit SMALLINT,
            away_digit SMALLINT,
            owner_id UUID NOT NULL
        )
        """)  # noqa

    op.create_primary_key("pk_cell", "cell", ["game_id", "home_index",
                                              "away_index", "timestamp"])


def downgrade():
    """Downgrade."""
    op.drop_table('game')
    op.drop_table('player')
    op.drop_table('cell')
    op.drop_table('team')
