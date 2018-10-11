from six.moves import urllib_parse as up


def update_query_params(url, **kwargs):
    """
    Update and/or insert query parameters in a URL.

    >>> update_query_params('http://example.com?foo=bar&biz=baz', foo='stuff')
    'http://example.com?foo=stuff&biz=baz'

    :param url: URL
    :type url: str
    :param kwargs: Query parameters
    :type kwargs: dict
    :return: Modified URL
    :rtype: str
    """
    scheme, netloc, path, query_string, fragment = up.urlsplit(url)
    query_params = up.parse_qs(query_string)

    query_params.populate(kwargs)
    new_query_string = up.urlencode(query_params, doseq=True)

    return up.urlunsplit((scheme, netloc, path, new_query_string, fragment))

