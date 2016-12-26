import copy
import os
import logging
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text
from werkzeug.exceptions import BadRequest

global _engine
_engine = None

log = logging.getLogger(__name__)


def get_timestamp_millis():
    """Return this client's notion of what time it is in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


def get_timestamp_from_value(value):
    """See if a value object has a timestamp and return it."""
    if isinstance(value, dict):
        return value.get('timestamp')


def get_latest_timestamp(value):
    """Get the later of either the value's timestamp, or now."""
    timestamp = get_timestamp_from_value(value)
    return max(timestamp or 0, get_timestamp_millis())


def get_db_url(db_name):
    """Get the URL for the database."""
    return 'postgresql://%s:%s@%s:%d/%s' % (
        os.environ.get('RDS_USERNAME', os.environ['POSTGRES_USER']),
        os.environ.get('RDS_PASSWORD', os.environ['PGPASSWORD']),
        os.environ.get('RDS_HOSTNAME', os.environ['POSTGRES_HOST']),
        os.environ.get('RDS_PORT', 5432),
        os.environ.get('RDS_DB_NAME', db_name),
    )


def init(db_url):
    """Initialize the Lucid bottleneck."""
    global _engine
    _engine = create_engine(db_url, pool_size=20, max_overflow=0)


def get_connection():
    global _engine
    return _engine.begin()


def deinit():
    """Uninitialize the package if necessary for testing."""
    global _engine
    _engine = None


def mock_bottleneck(f):
    """This will enable tests to not have to initialize the package."""
    try:
        from unittest.mock import patch
    except ImportError:
        from mock import patch

    def wrapper(*args, **kwargs):
        with patch('bottleneck.make_your_library_do_something', autospec=True):
            return f(*args, **kwargs)
    return wrapper


def clean_db(tables):
    with get_connection() as conn:
        query = sql_text("{truncates};SELECT 1"
                         .format(truncates=";".join("TRUNCATE TABLE %s" % table
                                                    for table in tables)))
        results = conn.execute(query).fetchall()
        assert results[0][0] == 1


def _colon_replacer(field, defaults):
    if field in defaults:
        return "DEFAULT"
    else:
        return ":%s" % field


def colonify(fields, defaults=None):
    """Returns a list with fields' items prefixed by a ':' character.

    If a field is in the defaults list, then it is replaced with 'DEFAULT'.
    """
    return [_colon_replacer(x, defaults or []) for x in fields]


class StorageError(Exception):
    """An error occurred during a storage operation."""
    pass


def get_item(conditions, table, fields, whitelist=None, timestamp=None):
    """Lookup an arbitrary Item from the database.

    If a timestamp exists, return the latest version up to that timestamp.
    """
    if isinstance(conditions, (UUID, str)):
        conditions = {'id': conditions}

    assert conditions and isinstance(conditions, dict)

    conditions_clause = ' AND '.join('%s=:%s' % (key, key)
                                     for key in conditions.keys())

    with get_connection() as conn:
        query = sql_text(
            """
            SELECT {field_names}
            FROM {table}
            WHERE {conditions_clause}
            {time_clause}
            ORDER BY timestamp DESC
            LIMIT 1
            """.format(
                field_names=', '.join(fields),
                table=table,
                time_clause='AND timestamp <= :timestamp' if timestamp else '',
                conditions_clause=conditions_clause,
            ))
        results = conn.execute(query, timestamp=timestamp,
                               **conditions).fetchall()

    if results and results[0]:
        return dict(zip(fields, results[0]))


def put_item(item, table, fields, primary_keys=('id',),
             defaults=('timestamp',)):
    """Place an item item into the database.

    Returns the full version from the database, including the id.
    """
    # defaults are the fields that will be set using the COLUMN's DEFAULT
    # expression
    item = {k: v for k, v in item.items()
            if k in fields}

    assert isinstance(primary_keys, (list, tuple)) and len(primary_keys) >= 1

    missing_keys = set(primary_keys) - set(item.keys())
    if missing_keys:
        raise StorageError('Missing keys: %s while putting %s into %s' % (
            missing_keys,
            item,
            table))

    for default in defaults:
        # Get rid of defaults
        item.pop(default, None)

    # Compute which fields are missing
    missing_fields = set(fields) - set(item.keys())

    if missing_fields != set(defaults):
        for default in defaults:
            missing_fields.discard(defaults)
        raise StorageError('Missing fields: %s while putting %s into %s' % (
            ', '.join(missing_fields),
            item,
            table))

    conditions_clause = ' AND '.join('%s=:%s' % (key, key)
                                     for key in primary_keys)
    with get_connection() as conn:
        query = sql_text(
            """
            INSERT INTO {table} ({field_names}) VALUES ({field_refs});
            SELECT {field_names}
            FROM {table}
            WHERE {conditions_clause}
            ORDER BY timestamp DESC
            LIMIT 1
            """.format(table=table,
                       conditions_clause=conditions_clause,
                       field_names=', '.join(fields),
                       field_refs=', '.join(colonify(fields,
                                                     defaults=defaults))))
        results = conn.execute(query, **item).fetchall()

    return dict(zip(fields, results[0]))


def get_latest_items(table, fields, conditions=None):
    """Retrieve many items from a table, with conditional filtering."""
    conditions = conditions or {}
    assert isinstance(conditions, dict)

    if conditions:
        conditions_clause = (
            ''.join(' AND %s=:%s' % (key, key)
                    for key in conditions.keys()))

    with get_connection() as conn:
        query = sql_text(
            """
            SELECT {field_names}
            FROM {table} t1
            WHERE t1.timestamp = (
                SELECT max(timestamp)
                FROM {table} t2
                WHERE t2.id = t1.id
                AND t2.timestamp <= CAST(
                    1000 * EXTRACT(EPOCH FROM NOW()) AS BIGINT))
            {conditions_clause}
            ORDER BY timestamp DESC
            """.format(
                field_names=', '.join(fields),
                table=table,
                conditions_clause=conditions_clause,
            ))
        results = conn.execute(query, **conditions).fetchall()

    if results:
        return [dict(zip(fields, row)) for row in results]
    else:
        return []


@contextmanager
def expanding(value, seen):
    if value in seen:
        raise BadRequest('Circular references found in data. See %s' % value)

    seen.add(value)
    try:
        yield
    finally:
        seen.remove(value)


def _path_join(x, y):
    """Concatenate two strings, delimited by a period."""
    if x:
        return '%s.%s' % (x, y)
    else:
        return str(y)


def _path_listify(path):
    return (path if path else '') + '[]'


def _in_whitelist(key, whitelist):
    if not whitelist:
        return True

    for regexp in whitelist:
        if regexp.match(key):
            return True

    return False


def _expand_dict(obj, timestamp, seen, expanders, whitelist, path):
    id_suffix = '_id'
    ids_suffix = '_ids'

    # Semantics here are interesting. Hierarchical root object's timestamp
    # is the one we pin to.
    timestamp = timestamp or obj.get('timestamp')
    for key, value in list(obj.items()):
        key_path = _path_join(path, key)
        if value is None or not _in_whitelist(key_path, whitelist):
            # Remove null values, and not whitelisted paths from the expansion
            obj.pop(key)
            continue

        # Do some basic serialization
        if isinstance(value, UUID):
            value = str(value)
            obj[key] = value

        if key.endswith(id_suffix):
            model = key[:-len(id_suffix)]

            if model in expanders:
                # We can remove the id
                obj.pop(key)

                # Now let's replace it with the expansion
                model_path = _path_join(path, model)
                expander = expanders[model]

                nested = get_item(value, expander['table'], expander['fields'],
                                  timestamp=timestamp)
                if nested:
                    assert model not in obj
                    with expanding(value, seen):
                        obj[model] = expand(nested, timestamp=timestamp,
                                            seen=seen, expanders=expanders,
                                            whitelist=whitelist,
                                            path=model_path)
                else:
                    log.warning({
                        'msg': 'failed-expansion',
                        'model_path': model_path,
                        'model': model,
                        'id': str(value),
                        'timestamp': timestamp,
                    })
                    raise StorageError('Failed expansion of %s: %s' % (
                        model, str(value)))

        elif key.endswith(ids_suffix):
            model = key[:-len(ids_suffix)]
            if model in expanders:
                # We can remove the id
                obj.pop(key)

                # Now let's replace it with the expansion
                models = model + 's'
                models_path = _path_join(path, _path_listify(models))
                expander = expanders[model]

                obj[models] = []
                assert isinstance(value, list)

                for subitem in value:
                    nested = get_item(subitem, expander['table'],
                                      expander['fields'], timestamp=timestamp)

                    if nested:
                        with expanding(subitem, seen):
                            obj[models] += [expand(nested, timestamp=timestamp,
                                                   seen=seen,
                                                   expanders=expanders,
                                                   whitelist=whitelist,
                                                   path=models_path)]
                    else:
                        log.warning({
                            'msg': 'failed-subitem-expansion',
                            'models_path': models_path,
                            'model': model,
                            'id': str(subitem),
                            'timestamp': timestamp,
                        })
                        raise StorageError(
                            'Failed sub-item expansion of %s' % str(value))

                # We should have expanded all of the items in the value list
                assert len(obj[models]) == len(value)

        else:
            expand(value, timestamp=timestamp, seen=seen, expanders=expanders,
                   whitelist=whitelist, path=key_path)

    return obj


def _expand_list(obj, timestamp, seen, expanders, whitelist, path):
    for index, item in enumerate(obj):
        obj[index] = expand(item, timestamp=timestamp, seen=seen,
                            expanders=expanders, whitelist=whitelist,
                            path=_path_listify(path))
    return obj


def expand(obj, latest=False, timestamp=None, seen=None, expanders=None,
           whitelist=None, path=''):
    """Expand any foo_id values into nested foo objects."""
    if latest:
        assert timestamp is None
        timestamp = get_latest_timestamp(obj)

    expanders = {} if expanders is None else expanders
    seen = set() if seen is None else seen

    # Recursively search the object tree for things we can expand.
    if isinstance(obj, dict):
        return _expand_dict(obj, timestamp, seen, expanders, whitelist, path)

    elif isinstance(obj, list):
        return _expand_list(obj, timestamp, seen, expanders, whitelist, path)

    elif isinstance(obj, tuple):
        return tuple(expand(x, timestamp=timestamp, seen=seen,
                            expanders=expanders, whitelist=whitelist,
                            path=_path_join(path, '()')) for x in obj)

    elif isinstance(obj, UUID):
        return str(obj)

    else:
        return obj


def serialize(obj, whitelist=None):
    """Do not expand anything, but run through expansion to get serialization.

    Prepares an object to be serialized as JSON.
    """
    obj = copy.deepcopy(obj)
    return expand(obj, whitelist=whitelist)
