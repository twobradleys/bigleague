GAMES = (
    'football',
    'basketball',
)


class GameState:
    pregame = 'pregame'
    playing = 'playing'
    canceled = 'canceled'
    complete = 'complete'


GAME_STATES = (
    GameState.pregame,
    GameState.playing,
    GameState.canceled,
    GameState.complete,
)


def get_sport_periods(sport):
    if sport == 'football':
        return [
            'Pregame',
            '1st quarter',
            '2nd quarter',
            '3rd quarter',
            'Final',
        ]
