# coding: utf-8
"""Tests for URL normalization"""
from __future__ import unicode_literals
from six import text_type
from unittest import TestCase

from ..normalizer import normalize_url


class UrlTestCase(TestCase):

    def test_normalized_urls(self):
        """Already normalized URLs should not change"""
        self.assertEqual(normalize_url("http://example.com/"),
                         "http://example.com/")

    def test_return_type(self):
        """Should return string"""
        assert isinstance(normalize_url("http://example.com/"), text_type)

    def test_append_slash(self):
        """Append a slash to the end of the URL if it's missing one"""
        self.assertEqual(normalize_url("http://example.com"),
                         "http://example.com/")

    def test_lower_case(self):
        """Normalized URL scheme and host are lower case"""
        self.assertEqual(normalize_url("HTTP://examPle.cOm/"),
                         "http://example.com/")
        self.assertEqual(normalize_url("http://example.com/A"),
                         "http://example.com/A")

    def test_strip_trailing_period(self):
        self.assertEqual(normalize_url("http://example.com."),
                         "http://example.com/")
        self.assertEqual(normalize_url("http://example.com./"),
                         "http://example.com/")

    def test_capitalize_escape_sequence(self):
        """All letters in percent-encoded triplets should be capitalized"""
        self.assertEqual(normalize_url("http://www.example.com/a%7b%7db"),
                         "http://www.example.com/a%7B%7Db")

    def test_path_percent_encoding(self):
        """All non-safe characters should be percent-encoded"""
        self.assertEqual(normalize_url("http://example.com/hello world{}"),
                         "http://example.com/hello%20world%7B%7D")

    def test_unreserved_percentencoding(self):
        """Unreserved characters should not be percent encoded. If they are, they
        should be decoded back; except in case of `/`, `?` and `#`"""
        self.assertEqual(normalize_url("http://www.example.com/%7Eusername/"),
                         "http://www.example.com/~username")
        self.assertEqual(normalize_url('http://example.com/foo%23bar'),
                         "http://example.com/foo%23bar")
        self.assertEqual(normalize_url('http://example.com/foo%2fbar'),
                         'http://example.com/foo%2Fbar')
        self.assertEqual(normalize_url('http://example.com/foo%3fbar'),
                         'http://example.com/foo%3Fbar')

    def test_remove_dot_segments(self):
        """Convert the URL path to an absolute path by removing `.` and `..`
        segments"""
        self.assertEqual(normalize_url("http://www.example.com/../a/b/../c/./d.html"),
                         "http://www.example.com/a/c/d.html")

    def test_remove_default_port(self):
        """Remove the default port for the scheme if it's present in the URL"""
        self.assertEqual(normalize_url("http://www.example.com:80/bar.html"),
                         "http://www.example.com/bar.html")
        self.assertEqual(normalize_url("HTTPS://example.com:443/abc/"),
                         "https://example.com/abc")

    def test_remove_empty_port(self):
        """Remove empty port from URL"""
        self.assertEqual(normalize_url("http://www.example.com:/"),
                         "http://www.example.com/")

    def test_remove_extra_slash(self):
        """Remove any extra slashes if present in the URl"""
        # TODO: Should we actually do this?
        # TODO: See https://webmasters.stackexchange.com/questions/8354/what-does-the-double-slash-mean-in-urls/8381#8381
        self.assertEqual(normalize_url("http://www.example.com/foo//bar.html"),
                         "http://www.example.com/foo/bar.html")
        self.assertEqual(normalize_url("http://example.com///abc"),
                         "http://example.com/abc")

    def test_query_string(self):
        """Query strings should be handled properly"""
        self.assertEqual(normalize_url("http://example.com/?a=1"),
                         "http://example.com/?a=1")
        self.assertEqual(normalize_url("http://example.com?a=1"),
                         "http://example.com/?a=1")
        self.assertEqual(normalize_url("http://example.com/a?b=1"),
                         "http://example.com/a?b=1")
        self.assertEqual(normalize_url("http://example.com/a/?b=1"),
                         "http://example.com/a?b=1")

    def test_dont_percent_encode_safe_chars_query(self):
        """Don't percent-encode safe characters in querystring"""
        self.assertEqual(normalize_url("http://example.com/a/?face=(-.-)"),
                         "http://example.com/a?face=(-.-)")

    def test_query_sorting(self):
        """Query strings should be sorted"""
        self.assertEqual(normalize_url('http://example.com/a?b=1&c=2'),
                         'http://example.com/a?b=1&c=2')
        self.assertEqual(normalize_url('http://example.com/a?c=2&b=1'),
                         'http://example.com/a?b=1&c=2')

    def test_query_string_spaces(self):
        """Spaces should be handled properly in query strings"""
        self.assertEqual(normalize_url("http://example.com/search?q=a b&a=1"),
                         "http://example.com/search?a=1&q=a+b")
        self.assertEqual(normalize_url("http://example.com/search?q=a+b&a=1"),
                         "http://example.com/search?a=1&q=a+b")
        self.assertEqual(normalize_url("http://example.com/search?q=a%20b&a=1"),  # noqa
                         "http://example.com/search?a=1&q=a+b")

    def test_drop_trailing_questionmark(self):
        """Drop the trailing question mark if no query string present"""
        self.assertEqual(normalize_url("http://example.com/?"),
                         "http://example.com/")
        self.assertEqual(normalize_url("http://example.com?"),
                         "http://example.com/")
        self.assertEqual(normalize_url("http://example.com/a?"),
                         "http://example.com/a")
        self.assertEqual(normalize_url("http://example.com/a/?"),
                         "http://example.com/a")

    def test_percent_encode_querystring(self):
        """Non-safe characters in query string should be percent-encoded"""
        self.assertEqual(normalize_url("http://example.com/?a=hello{}"),
                         "http://example.com/?a=hello%7B%7D")

    def test_normalize_percent_encoding_in_querystring(self):
        """Percent-encoded querystring should be uppercased"""
        self.assertEqual(normalize_url("http://example.com/?a=b%7b%7d"),
                         "http://example.com/?a=b%7B%7D")

    def test_unicode_query_string(self):
        """Unicode query strings should be converted to bytes using uft-8 encoding
        and then properly percent-encoded"""
        self.assertEqual(normalize_url("http://example.com/?file=résumé.pdf"),
                         "http://example.com/?file=r%C3%A9sum%C3%A9.pdf")

    def test_unicode_path(self):
        """Unicode path should be converted to bytes using utf-8 encoding and then
        percent-encoded"""
        self.assertEqual(normalize_url("http://example.com/résumé"),
                         "http://example.com/r%C3%A9sum%C3%A9")

    def test_idna(self):
        """International Domain Names should be normalized to safe characters"""
        self.assertEqual(normalize_url("http://ドメイン.テスト"),
                         "http://xn--eckwd4c7c.xn--zckzah/")
        self.assertEqual(normalize_url("http://Яндекс.рф"),
                         "http://xn--d1acpjx3f.xn--p1ai/")

    def test_dont_change_username_password(self):
        """Username and password shouldn't be lowercased"""
        self.assertEqual(normalize_url("http://Foo:BAR@exaMPLE.COM/"),
                         "http://Foo:BAR@example.com/")

    def test_normalize_ipv4(self):
        """Normalize ipv4 URLs"""
        assert normalize_url("http://192.168.0.1/") == "http://192.168.0.1/"
        assert (normalize_url("http://192.168.0.1:8080/a?b=1") ==
                "http://192.168.0.1:8080/a?b=1")
        assert normalize_url("192.168.0.1") == "http://192.168.0.1/"
        assert (normalize_url("192.168.0.1:8080/a/b/c") ==
                "http://192.168.0.1:8080/a/b/c")

    def test_normalize_ipv6(self):
        """Normalize ipv6 URLs"""
        assert normalize_url("[::1]") == "http://[::1]/"
        assert normalize_url("http://[::1]") == "http://[::1]/"
        assert normalize_url("[::1]:8080") == "http://[::1]:8080/"
        assert normalize_url("http://[::1]:8080") == "http://[::1]:8080/"

    def test_strip_leading_trailing_whitespace(self):
        """Strip leading and trailing whitespace if any"""
        assert normalize_url("   http://example.com  ") == "http://example.com/"
        assert normalize_url("http://example.com/a  ") == "http://example.com/a"
        assert normalize_url("   http://example.com/") == "http://example.com/"

    def test_non_ideal_inputs(self):
        """Not the ideal input; but we should handle it anyway"""
        assert normalize_url("example.com") == "http://example.com/"
        assert normalize_url("example.com/abc") == "http://example.com/abc"
        assert normalize_url("//example.com/abc") == "http://example.com/abc"

    def test_additional_query_args(self):
        """Add any additional query arguments to the URL"""
        self.assertEqual(normalize_url("http://example.com?c=d", [("a", "b")]),
                         "http://example.com/?a=b&c=d")
        self.assertEqual(normalize_url("http://example.com", [("a", "b")]),
                         "http://example.com/?a=b")
        self.assertEqual(normalize_url("http://example.com", [("résumé", "résumé")]),
                         "http://example.com/?r%C3%A9sum%C3%A9=r%C3%A9sum%C3%A9")

    def test_non_urls(self):
        """If a non-URL string is passed, return None"""
        assert normalize_url("") is None
        assert normalize_url("abc xyz") is None
        assert normalize_url("asb#abc") is None
        assert normalize_url("Яндекс.рф") is not None
        assert normalize_url("google.blog") is not None
        assert normalize_url("http//google.com") is None
        assert normalize_url("http://user@pass:example.com") is None

    def test_drop_fragments(self):
        """Drop or keep fragments based on the option passed"""
        assert (normalize_url("http://example.com/a?b=1#frag")
                == "http://example.com/a?b=1")
        assert (normalize_url("http://example.com/a?b=1#frag", drop_fragments=False)
                == "http://example.com/a?b=1#frag")

    def test_non_string_input(self):
        """Non-string input should produce None as result"""
        assert normalize_url(None) is None
        assert normalize_url([]) is None
        assert normalize_url(123) is None
