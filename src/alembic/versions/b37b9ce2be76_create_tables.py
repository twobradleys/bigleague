"""Create the tables."""
from alembic import op
from sqlalchemy.sql import column

from bigleague.storage.offers import OFFER_TYPES, OFFER_STATES
from bigleague.lib.sports import GAME_STATES, GAMES
from bigleague.lib.house import HOUSE_PLAYER_ID

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
    create_offer_table()


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
    op.create_check_constraint(
        "ck_team",
        "team",
        column('sport').in_(GAMES))


def create_offer_table():
    op.execute("""
        CREATE TABLE offer (
            game_id UUID NOT NULL,
            home_index SMALLINT NOT NULL,
            away_index SMALLINT NOT NULL,
            player_id UUID NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            type VARCHAR(8) NOT NULL,
            price INT NOT NULL,
            state VARCHAR(8) NOT NULL,
            counterparty_player_id UUID,
            timestamp_filled BIGINT,
            counterparty_price INT
        )""")  # noqa
    op.create_primary_key("pk_offer", "offer", ["game_id", "home_index",
                                                "away_index", "player_id",
                                                "timestamp"])
    op.create_check_constraint(
        "ck_offer",
        "offer",
        column('type').in_(OFFER_TYPES)
        & column('state').in_(OFFER_STATES))

# TODO: create IRL game events table


def create_game_table():
    # TODO: consider refactoring event_name into an event table
    op.execute("""
        CREATE TABLE game (
            id UUID NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            event_name VARCHAR(256) NOT NULL,
            sport VARCHAR(64) NOT NULL,
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
        & column('sport').in_(GAMES)
        & (column('home_team_id') != column('away_team_id')))

    op.create_primary_key("pk_game", "game", ["id", "timestamp"])


def create_player_table():
    op.execute("""
        CREATE TABLE player (
            id UUID NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            handle VARCHAR(64) NOT NULL,
            auth_token UUID
        )
        """)  # noqa

    op.create_primary_key("pk_player", "player", ["id"])
    op.create_unique_constraint("uq_player", "player", ["handle"])
    op.execute("""
        INSERT INTO player (id, handle, auth_token) VALUES (
            '%s',
            'house',
            NULL)""" % HOUSE_PLAYER_ID)


# TODO: many-to-many of players + games + funds

# TODO: offers table

def create_cell_table():
    op.execute("""
        CREATE TABLE cell (
            game_id UUID NOT NULL,
            home_index SMALLINT NOT NULL,
            away_index SMALLINT NOT NULL,
            timestamp BIGINT DEFAULT CAST(1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT) NOT NULL,
            home_digit SMALLINT,
            away_digit SMALLINT,
            player_id UUID NOT NULL
        )
        """)  # noqa

    op.create_primary_key("pk_cell", "cell", ["game_id", "home_index",
                                              "away_index", "timestamp"])


def downgrade():
    """Downgrade."""
    op.execute("""DROP TABLE IF EXISTS game""")
    op.execute("""DROP TABLE IF EXISTS player""")
    op.execute("""DROP TABLE IF EXISTS cell""")
    op.execute("""DROP TABLE IF EXISTS team""")
    op.execute("""DROP TABLE IF EXISTS offer""")
