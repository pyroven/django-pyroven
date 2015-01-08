#   Copyright 2011 Andrew Ryrie (amr66)

"""
Provides the backend for the Django Pyroven
"""

import traceback

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from pyroven import (MalformedResponseError, InvalidResponseError,
                     RavenResponse, PublicKeyNotFoundError)

from pyroven.utils import setting


class HttpResponseSeeOther(HttpResponseRedirect):
    """An HttpResponse with a 303 status code, since django doesn't provide one
    by default.  A 303 is required by the the WAA2WLS specification."""
    status_code = 303


class RavenAuthBackend(object):
    """An authentication backend for django that uses Raven.  To use, add
    'pyroven.backends.RavenAuthBackend' to AUTHENTICATION_BACKENDS
    in your django settings.py."""

    def authenticate(self, response_str=None):
        """Checks a response from the Raven server and sees if it is valid.  If
        it is, returns the User with the same username as the Raven username.
        @return User object, or None if authentication failed"""

        if response_str is None:
            return None

        response = RavenResponse(response_str)

        # Check that everything is correct, and return
        try:
            response.validate()
        except MalformedResponseError:
            print("Got a malformed response from the Raven server")
            # If the response was malformed, we're not allowed to login
            return None
        except InvalidResponseError:
            print("Got an invalid reponse from the Raven server")
            return None
        except PublicKeyNotFoundError:
            print("Cannot find a public key for the server's response")
            return None
        except Exception:
            traceback.print_exc()
            return None

        username = response.principal

        if username is None:
            return None

        user = self.get_user_by_name(username)
        return user

    def get_user_by_name(self, username):
        """Gets a user with the specified username from the DB."""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print("Successfully authenticated as %s in Raven, but that user "
                  "does not exist in Django" % username)

            if setting('PYROVEN_CREATE_USER', default=False):
                print("Creating user for %s" % username)
                user = User(username=username)
                user.set_unusable_password()
                user.save()
                return user
            else:
                print("User %s not created" % username)

            return None
        else:
            print("%s successfully authenticated via Raven" % username)
            return user

    def get_user(self, user_id):
        """Gets a user with the specified user ID from the DB.  For some
        reason, this is required by django for an auth backend."""
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            print("No such user: %s" % user_id)
            return None
        else:
            return user
