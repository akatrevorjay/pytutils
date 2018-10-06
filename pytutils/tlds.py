import cachetools

from .pythree import ensure_decoded_text
from itertools import accumulate

_ttl_cache = cachetools.TTLCache(maxsize=1024, ttl=600)


# This is cached because tldextract is SLOW
@cachetools.cachedmethod(_ttl_cache)
def split_domain_into_subdomains(domain, split_tld=False):
    import tldextract

    # Requires unicode
    domain = ensure_decoded_text(domain)

    # Do not request latest TLS list on init == suffix_list_url=False
    global _tldex
    if _tldex is None:
        _tldex = tldextract.TLDExtract(suffix_list_url=False)

    tx = _tldex(domain)

    domains = []
    if tx.subdomain:
        domains.extend(tx.subdomain.split('.'))

    # tx.registered_domain returns only if domain AND suffix are not none
    # There are cases where we have domain and not suffix; ie short hostnames
    registered_domain = [tx.domain]
    if tx.suffix:
        registered_domain.append(tx.suffix)

    if split_tld:
        domains.extend(registered_domain)
    else:
        domains.append('.'.join(registered_domain))

    # Musical chairs. Change places!
    domains.reverse()

    def join_dom(a, b):
        return '.'.join([b, a])

    # Take each part and add it to the previous part, returning all results
    domains = list(accumulate(domains, func=join_dom))
    # Change places!
    domains.reverse()

    return domains
