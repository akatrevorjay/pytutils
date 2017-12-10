"""
Random utilities that I should stop copying across project boundaries, hence this exists.

~trevorj https://github.com/akatrevorjay/pytutils
"""

from . import mappings, system, pythree, files, meth, pretty, queues, rand, iterators

# ease the burden for those deemed important enough
from .mappings import ProxyMutableMapping, MultiDict, format_dict_recursively
from .system import PyInfoMinimal, PyInfo
from .files import islurp, burp
from .meth import bind
from .pretty import pf, pp, pprint, pformat
