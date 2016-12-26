GAME_STATES = (
    'pregame',
    'playing',
    'canceled',
    'complete',
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
