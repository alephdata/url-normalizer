import string

# Reserved delimeters from https://tools.ietf.org/html/rfc3986#section-2.2
GEN_DELIMS = ":/?#[]@"
SUB_DELIMS = "!$&'()*+,;="
RESERVED_CHARS = GEN_DELIMS + SUB_DELIMS

# Unreserved characters from https://tools.ietf.org/html/rfc3986#section-2.3
UNRESERVED_CHARS = string.ascii_letters + string.digits + "-._~"

SAFE_CHARS = RESERVED_CHARS + UNRESERVED_CHARS + '%'

# TODO: Add more schemes may be
DEFAULT_PORTS = {
    "http": 80,
    "https": 443
}

SCHEMES = ("http", "https")
