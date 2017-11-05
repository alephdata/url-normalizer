from urlnormalizer.utils import _urlencode


def query_string(items):
    """Given a list of tuples, returns a query string for URL building."""
    query = [(k, v) for (k, v) in items if v is not None]
    if not len(query):
        return ''
    return '?' + _urlencode(query)
