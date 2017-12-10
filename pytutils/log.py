import logging
import logging.config
import inspect
import sys
import os


class _PyInfo(object):
    PY2 = sys.version_info[0] == 2
    PY3 = sys.version_info[0] == 3

    if PY3:
        string_types = str,
        text_type = str
        binary_type = bytes
    else:  # PY2
        string_types = basestring,
        text_type = unicode
        binary_type = str


def _namespace_from_calling_context():
    """
    Derive a namespace from the module containing the caller's caller.

    :return: the fully qualified python name of a module.
    :rtype: str
    """
    # Not py3k compat
    # return inspect.currentframe(2).f_globals["__name__"]
    # TODO Does this work in both py2/3?
    return inspect.stack()[2][0].f_globals["__name__"]


DEFAULT_CONFIG = dict(
    level=logging.INFO,
    format=' '.join(
        [
            '%(asctime)s|',
            '%(name)s/%(processName)s[%(process)d]-%(threadName)s[%(thread)d]:'
            '%(message)s @%(funcName)s:%(lineno)d #%(levelname)s',
        ]
    ),
)


def get_config(given=None, env_var=None, default=None):
    config = given

    if not config and env_var:
        config = os.environ.get(env_var)

    if not config and default:
        config = default

    if config is None:
        raise ValueError('Invalid logging config: %s' % config)

    if isinstance(config, _PyInfo.string_types):
        import json

        try:
            config = json.loads(config)
        except ValueError:
            import yaml

            try:
                config = yaml.load(config)
            except ValueError:
                raise ValueError("Could not parse logging config as bare, json," " or yaml: %s" % config)

    return config


def configure(config=None, env_var='LOGGING', default=DEFAULT_CONFIG):
    cfg = get_config(config, env_var, default)
    logging.config.dictConfig(**cfg)


_CONFIGURED = []


def _ensure_configured(_has_configured=_CONFIGURED):
    if _has_configured:
        return

    configure()
    _has_configured.append(True)


def get_logger(name=None):
    _ensure_configured()

    if not name:
        name = _namespace_from_calling_context()

    return logging.getLogger(name)
