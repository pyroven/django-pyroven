"""Base configuration for Raven logins
"""
import time
import urllib

from OpenSSL.crypto import FILETYPE_PEM, load_certificate, verify

from pyroven.utils import decode_sig, setting, parse_time


class MalformedResponseError(Exception):
    """Raised if a response from the raven server is malformed."""
    pass


class InvalidResponseError(Exception):
    """Raised if the response from the server is parseable but still not
    valid"""
    pass


class PublicKeyNotFoundError(Exception):
    """Raised if the server signs the response with a key which we don't have
    the public part of"""
    pass


class RavenResponse(object):
    """Represents a response from the raven server.  Contains fields for
    version number, status, etc. and methods for checking the validity of the
    response via the RSA signature."""

    ver = None
    status = None
    msg = None
    issue = None
    ident = None
    url = None
    principal = None
    auth = None
    sso = None
    life = None
    params = None
    kid = None
    sig = None
    config = None

    STATUS = {200: 'Successful authentication',
              410: 'User cancelled authentication',
              510: 'No mutually acceptable authentication types available',
              520: 'Unsupported protocol version',
              530: 'General request parameter error',
              540: 'Interaction would be required',
              560: 'WAA not authorised to use this WLS',
              570: 'Authentication declined'}

    def __init__(self, response_str):
        """Makes a Ravenresponse object from a reponse string passed with
        HTTP GET.
        @param reponse_str The response string, normally passed as
        GET['WLS-Response']
        """
        PYROVEN_RETURN_URL = setting('PYROVEN_RETURN_URL')
        PYROVEN_VER = setting('PYROVEN_VERSION', 2)
        PYROVEN_MAX_CLOCK_SKEW = setting('PYROVEN_MAX_CLOCK_SKEW', 2)
        PYROVEN_TIMEOUT = setting('PYROVEN_TIMEOUT', 10)
        PYROVEN_AAUTH = setting('PYROVEN_AAUTH', ['pwd', 'card'])
        PYROVEN_IACT = setting('PYROVEN_IACT', False)
        PYROVEN_CERTS = setting('PYROVEN_CERTS')

        # The response is a !-separated list of variables, so split it by !
        tokens = response_str.split('!')

        # Check we have the right version
        try:
            self.ver = int(tokens[0])
        except ValueError:
            print("Version is not integer")
            raise MalformedResponseError("Version number must be integer")

        if self.ver != PYROVEN_VER:
            print("Version number doesn't match config")
            raise MalformedResponseError("Version number does not match that "
                                         "in the configuration")

        if self.ver < 1 or self.ver > 2:
            print("Version number not supported")
            raise MalformedResponseError("Unsupported version: %d" % self.ver)

        if len(tokens) != 13:
            print("wrong number params in response")
            raise MalformedResponseError("Wrong number of parameters in "
                                         "response: expected 13, got %d"
                                         % len(tokens))

        # Get all the tokens from the request
        try:
            self.status = int(tokens[1])
        except ValueError:
            print("status code must be integer")
            raise MalformedResponseError(
                "Status code must be an integer, not %s" % tokens[1]
            )
        self.msg = tokens[2]
        try:
            self.issue = parse_time(tokens[3])
        except ValueError:
            print("Issue time is not a valid raven time")
            raise MalformedResponseError(
                "Issue time is not a valid Raven time, not %s" % tokens[3]
            )
        self.ident = tokens[4]
        self.url = urllib.unquote(tokens[5])
        self.principal = tokens[6]
        self.auth = tokens[7]
        self.sso = tokens[8]
        if tokens[9] == "":
            self.life = None
        else:
            try:
                self.life = int(tokens[9])
            except ValueError:
                print("lifetime is not an integer")
                raise MalformedResponseError("Life must be an integer, not %s"
                                             % tokens[9])
        self.params = tokens[10]
        self.kid = tokens[11]
        self.sig = decode_sig(tokens[12])

        # Check that the URL is as expected
        if self.url != PYROVEN_RETURN_URL:
            print("URL does not match")
            raise InvalidResponseError(
                "The URL in the response does not match the URL expected"
            )

        # Check that the issue time is not in the future or too far in the past
        if self.issue > time.time() + PYROVEN_MAX_CLOCK_SKEW:
            print("Timestamp in future")
            raise InvalidResponseError("The timestamp on the response is in "
                                       "the future")
        if self.issue < time.time() - PYROVEN_MAX_CLOCK_SKEW - PYROVEN_TIMEOUT:
            print(
                "Response has timed out - issued %s, now %s" % (
                    time.asctime(time.gmtime(self.issue)),
                    time.asctime()
                )
            )
            raise InvalidResponseError("The response has timed out")

        # Check that the type of authentication was acceptable
        print("Checking authentication types")
        if self.auth != "":
            # Authentication was done recently with this auth type
            if PYROVEN_AAUTH is not None:
                # if PYROVEN_AAUTH == None, any type of authentication is
                # acceptable
                if self.auth not in PYROVEN_AAUTH:
                    print("Wrong type of auth")
                    raise InvalidResponseError("The reponse used the wrong "
                                               "type of authentication")
        elif self.sso != "" and not PYROVEN_IACT:
            # Authentication was not done recently, and that is acceptable
            if PYROVEN_IACT is not None:

                # Get the list of auth types used on previous occasions and
                # check that at least one of them is acceptable
                auth_good = False
                for auth_type in self.sso.split(','):
                    if auth_type in PYROVEN_AAUTH:
                        auth_good = True
                        break

                # If none of the previous types match one we asked for, raise
                # an error
                if not auth_good:
                    print("Wrong type of auth")
                    raise InvalidResponseError("The response used the wrong "
                                               "type of authentication")
        else:
            if PYROVEN_IACT:
                # We had required an interactive authentication, but didn't get
                # one
                print("Interactive authentication required")
                raise InvalidResponseError("Interactive authentication "
                                           "required but not received")
            else:
                # Both auth and sso are empty, which is not allowed
                print("no authentication types supplied")
                raise MalformedResponseError(
                    "No authentication types supplied"
                )
        # Done checking the authentication type was acceptable

        # Check that the signature is correct - first get the certificate
        print("Checking signature")
        try:
            cert = load_certificate(FILETYPE_PEM, PYROVEN_CERTS[self.kid])
        except KeyError:
            print("unknown public key")
            raise PublicKeyNotFoundError("We do not have the public key "
                                         "corresponding to the key the server "
                                         "signed the response with")

        # Create data string used for hash
        # http://raven.cam.ac.uk/project/waa2wls-protocol.txt
        data = '!'.join(tokens[0:11])

        # Check that it matches
        try:
            verify(cert, self.sig, str(data), 'sha1')
        except Exception:
            raise InvalidResponseError(
                "The signature for this response is not valid."
            )

    def validate(self):
        """Returns True if this represents a successful authentication;
        otherwise returns False."""
        return self.status == 200
