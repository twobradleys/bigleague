import os.path
import json
import os
import yaml
import logging.config
from copy import deepcopy

from .serialize import serialize
from pythonjsonlogger import jsonlogger


def dict_merge(a, b):
    """Recursively merge two dictionaries."""
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


class ConfigurationError(Exception):
    pass


class Configuration(object):
    """Manages global configuration from YAML files."""

    def __init__(self):
        self.path = None
        self.config = {}

    def load(self):
        """Load config file and recurse up "extends" path to base config.

        Raises ConfigurationError if the environment is not set or if the
        config path does not exist.
        """
        self.config = {}

        if 'APP_CONFIG' not in os.environ:
            raise ConfigurationError('APP_CONFIG is not specified')

        self.path = os.environ['APP_CONFIG']
        self.path = os.path.expandvars(self.path)
        self.path = os.path.abspath(self.path)
        self.name = os.path.basename(self.path).split('.')[0]

        if not os.path.exists(self.path):
            raise ConfigurationError(
                'You specified APP_CONFIG to be at %s, but that file does '
                'not exist!'
                % (self.path,)
            )

        self.config = self.load_from_file(self.path)

    def load_from_file(self, filename):
        """Load configuration from the given filename."""
        try:
            config = self._load_from_file(filename)
            if not config:
                raise ValueError('Empty config')
            return config

        except ValueError as e:
            raise ConfigurationError(
                'Error loading config from %s: %s'
                % (filename, str(e))
            )

    @staticmethod
    def _load_from_file(filename):
        """Internal recursive file loader."""
        if not os.path.exists(filename):
            raise Exception('{0} does not exist'.format(filename))
        with open(filename, 'r') as f:
            config = yaml.safe_load(f)

        extends = config.pop('extends', None)
        if extends:
            extends = os.path.abspath(
                os.path.join(os.path.dirname(filename), extends))
            config = dict_merge(Configuration._load_from_file(extends), config)

        return config

    def get(self, key, default=None):
        """Get the configuration for a specific variable, using dots as
        delimiters for nested objects. Example: config.get('api.host')
        returns the value of self.config['api']['host'] or None if any
        of those keys does not exist. The default return value can be
        overridden.
        """
        value = self.config
        for k in key.split('.'):
            try:
                value = value[k]
            except KeyError:
                return default

        return value


CONFIG = Configuration()
CONFIG.load()


def get(*args, **kwargs):
    return CONFIG.get(*args, **kwargs)


def init(app_id, root_log_level=logging.WARNING, app_log_level=logging.DEBUG):
    """Initialize the config module.

    app_id should be the base name that you use in all of your loggers, that is
    one above 'root'.
    """
    if not app_id:
        raise Exception("You must initialize the config module with an app_id.")

    root_logger = logging.getLogger()
    log_handler = logging.StreamHandler()
    supported_keys = [
        'created',
        'filename',
        'funcName',
        'levelname',
        'levelno',
        'lineno',
        'module',
        'message',
        'pathname',
        'process',
        'processName',
        'thread',
        'threadName',
        'name',
    ]

    custom_format = ' '.join(
        ['%({0:s})'.format(i) for i in supported_keys])

    formatter = jsonlogger.JsonFormatter(
        custom_format,
        json_default=serialize,
        json_encoder=json.JSONEncoder)
    log_handler.setFormatter(formatter)

    root_logger.addHandler(log_handler)
    root_logger.setLevel(root_log_level)

    app_logger = logging.getLogger(app_id)
    app_logger.setLevel(app_log_level)
