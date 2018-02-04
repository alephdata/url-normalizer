"""This module contains functions to help normalize URLs"""
from __future__ import unicode_literals
import six
from os.path import normpath
from six.moves.urllib.parse import urlunsplit
from six.moves.urllib.parse import urlsplit

from urlnormalizer.utils import _parse_qsl, _urlencode, _quote, _unquote
from urlnormalizer.validator import is_valid_url
from urlnormalizer.constants import SCHEMES, DEFAULT_PORTS


def normalize_url(url, extra_query_args=None, drop_fragments=True):
    """Normalize a url to its canonical form.

    Parameters
    ----------
    url: str
        URL to be normalize
    extra_query_args: list of 2-element str tuples, optional
        A list of tuples with further query arguments that need to be appended
        to the URL
    drop_fragments: boolean
        Keep or drop url fragments

    Returns
    -------
    str
        A normalized url with supplied extra query arguments
    None
        If the passed string doesn't look like a URL, return None
    """
    if not isinstance(url, six.string_types):
        return None
    url = url.strip()
    if not url.lower().startswith(SCHEMES):
        if url.startswith("//"):
            url = "http:" + url
        else:
            url = "http://" + url
    if not is_valid_url(url):
        # Doesn't look like a valid URL
        return None
    parts = urlsplit(url)

    scheme, netloc, path, query, fragment, username, password, port = (
        parts.scheme, parts.netloc, parts.path, parts.query,
        parts.fragment, parts.username, parts.password, parts.port
    )

    # normalize parts
    path = _normalize_path(path)
    netloc = _normalize_netloc(scheme, netloc, username, password, port)
    query = _normalize_query(query, extra_query_args)

    if drop_fragments:
        fragment = ""

    # Put the url back together
    url = urlunsplit((scheme, netloc, path, query, fragment))
    return url


def _normalize_path(path):
    # If there are any `/` or `?` or `#` in the path encoded as `%2f` or `%3f`
    # or `%23` respectively, we don't want them unquoted. So escape them
    # before unquoting
    for reserved in ('2f', '2F', '3f', '3F', '23'):
        path = path.replace('%' + reserved, '%25' + reserved.upper())
    # unquote and quote the path so that any non-safe character is
    # percent-encoded and already percent-encoded triplets are upper cased.
    unquoted_path = _unquote(path)
    path = _quote(unquoted_path) or "/"
    trailing_slash = "/" == path[-1]
    # Use `os.path.normpath` to normalize paths i.e. remove duplicate `/` and
    # make the path absolute when `..` or `.` segments are present.
    # TODO: Should we remove duplicate slashes?
    # TODO: See https://webmasters.stackexchange.com/questions/8354/what-does-the-double-slash-mean-in-urls/8381#8381
    path = normpath(path)
    # normpath strips trailing slash. Add it back if it was there because
    # this might make a difference for URLs.
    if trailing_slash and not path.endswith('/'):
        path = path + "/"
    # POSIX allows one or two initial slashes, but treats three or more
    # as single slash.So if there are two initial slashes, make them one.
    if path.startswith('//'):
        path = '/' + path.lstrip('/')
    return path


def _normalize_netloc(scheme, netloc, username, password, port):
    # Leave auth info out before fiddling with netloc
    auth = None
    if username:
        auth = username
        if password:
            auth += ":" + password
        netloc = netloc.split(auth)[1][1:]
    # Handle international domain names
    netloc = netloc.encode("idna").decode("ascii")
    # normalize to lowercase and strip empty port or trailing period if any
    netloc = netloc.lower().rstrip(":").rstrip(".")
    # strip default port
    if port and DEFAULT_PORTS.get(scheme) == port:
        netloc = netloc.rstrip(":" + str(port))
    # Put auth info back in
    if auth:
        netloc = auth + "@" + netloc
    return netloc


def _normalize_query(query, extra_query_args):
    # Percent-encode and sort query arguments.
    queries_list = _parse_qsl(query)
    # Add the additional query args if any
    if extra_query_args:
        for (name, val) in extra_query_args:
            queries_list.append((name, val))
    return _urlencode(queries_list)
