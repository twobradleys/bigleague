import bottleneck


def get_tables():
    """Get this app's tables."""
    return [
        'game',
        'player',
        'cell',
        'team',
    ]


bottleneck.init(db_url=bottleneck.get_db_url('bigleague'))
