import time
import calendar

from string import maketrans
from base64 import b64decode

from django.conf import settings
from django.http import HttpResponseRedirect


def decode_sig(sig):
    """Decodes a signature from the variant base64 used by raven.
    @param sig  A string giving the signature in Raven's variant base-64
    @return  A binary string containing the signature"""
    table = maketrans("-._", "+/=")
    sig = str(sig).translate(table)
    try:
        return b64decode(sig)
    except TypeError:
        raise MalformedResponseError(  # noqa
            "Signature is not a valid base-64 encoded string"
        )


def setting(name, default=None):
    """Returns a setting from the Django settings file"""
    return getattr(settings, name, default)


def parse_time(time_string):
    """Converts a time of the form '20110729T123456Z' to a number of seconds
    since the epoch.
    @exception ValueError if the time is not a valid Raven time"""
    return calendar.timegm(time.strptime(time_string, "%Y%m%dT%H%M%SZ"))


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303
