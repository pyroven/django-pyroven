**Deprecated and superseded by https://gitlab.developers.cam.ac.uk/uis/devops/django/ucamwebauth**

# Pyroven: Cambridge University Raven integration for Django

[![Build Status](https://travis-ci.org/pyroven/django-pyroven.svg?branch=master)](https://travis-ci.org/pyroven/django-pyroven)

pyroven is a library which provides use of Cambridge University's [Raven authentication](http://raven.cam.ac.uk/) for [Django](https://www.djangoproject.com/). It provides a Django authentication backend which can be added to `AUTHENTICATION_BACKENDS` in the Django `settings` module.

## Use

Install django-pyroven using pip:

```bash
pip install django-pyroven
```

Then you can enable it within your Django project's settings.py:

```python
AUTHENTICATION_BACKENDS = (
    'pyroven.backends.RavenAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)
```

This allows both normal Django login and Raven login.

You should then enable the URLs for pyroven:

````python
urlpatterns = patterns('',
    ...
    url(r'', include('pyroven.urls')),
    ...
)
````

## Minimum Config Settings

You then need to configure the app's settings. Raven has a live and test environments, the URL and certificate details are given below.

There are four minimum config settings:

```python
PYROVEN_LOGIN_URL: a string representing the URL for the Raven login redirect.
PYROVEN_LOGOUT_URL: a string representing the logout URL for Raven
PYROVEN_RETURN_URL: the URL of your app which the Raven service should 
    return the user to after authentication
PYROVEN_CERTS: a dictionary including key names and their associated 
    certificates which can be downloaded from the Raven project pages.
```

The final major setting is:

```python
PYROVEN_CREATE_USER = False
```

This defaults to False, but when True, allows the autocreation of users who have been successfully authenticated by Raven, but do not exist in the local database. The user is created with set_unusable_password().

An example, referencing the Raven test environment is given below:

```python
PYROVEN_LOGIN_URL = 'https://demo.raven.cam.ac.uk/auth/authenticate.html'
PYROVEN_LOGOUT_URL = 'https://demo.raven.cam.ac.uk/auth/logout.html'
PYROVEN_RETURN_URL = 'http://your.example.com/raven_return/'
PYROVEN_CERTS = {'901': """-----BEGIN CERTIFICATE-----
MIIDzTCCAzagAwIBAgIBADANBgkqhkiG9w0BAQQFADCBpjELMAkGA1UEBhMCR0Ix
EDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEgMB4GA1UEChMX
VW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1dGluZyBTZXJ2
aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4gREVNTyBwdWJs
aWMga2V5IDEwHhcNMDUwNzI2MTMyMTIwWhcNMDUwODI1MTMyMTIwWjCBpjELMAkG
A1UEBhMCR0IxEDAOBgNVBAgTB0VuZ2xhbmQxEjAQBgNVBAcTCUNhbWJyaWRnZTEg
MB4GA1UEChMXVW5pdmVyc2l0eSBvZiBDYW1icmlkZ2UxLTArBgNVBAsTJENvbXB1
dGluZyBTZXJ2aWNlIERFTU8gUmF2ZW4gU2VydmljZTEgMB4GA1UEAxMXUmF2ZW4g
REVNTyBwdWJsaWMga2V5IDEwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBALhF
i9tIZvjYQQRfOzP3cy5ujR91ZntQnQehldByHlchHRmXwA1ot/e1WlHPgIjYkFRW
lSNcSDM5r7BkFu69zM66IHcF80NIopBp+3FYqi5uglEDlpzFrd+vYllzw7lBzUnp
CrwTxyO5JBaWnFMZrQkSdspXv89VQUO4V4QjXV7/AgMBAAGjggEHMIIBAzAdBgNV
HQ4EFgQUgjC6WtA4jFf54kxlidhFi8w+0HkwgdMGA1UdIwSByzCByIAUgjC6WtA4
jFf54kxlidhFi8w+0HmhgaykgakwgaYxCzAJBgNVBAYTAkdCMRAwDgYDVQQIEwdF
bmdsYW5kMRIwEAYDVQQHEwlDYW1icmlkZ2UxIDAeBgNVBAoTF1VuaXZlcnNpdHkg
b2YgQ2FtYnJpZGdlMS0wKwYDVQQLEyRDb21wdXRpbmcgU2VydmljZSBERU1PIFJh
dmVuIFNlcnZpY2UxIDAeBgNVBAMTF1JhdmVuIERFTU8gcHVibGljIGtleSAxggEA
MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEEBQADgYEAsdyB+9szctHHIHE+S2Kg
LSxbGuFG9yfPFIqaSntlYMxKKB5ba/tIAMzyAOHxdEM5hi1DXRsOok3ElWjOw9oN
6Psvk/hLUN+YfC1saaUs3oh+OTfD7I4gRTbXPgsd6JgJQ0TQtuGygJdaht9cRBHW
wOq24EIbX5LquL9w+uvnfXw=
-----END CERTIFICATE-----
""")
```

## Additional Config Settings

Extra settings which can be used to fine tune the performance of django-pyroven include: 

```python
PYROVEN_MAX_CLOCK_SKEW = ''
PYROVEN_TIMEOUT = ''
PYROVEN_IACT = ''
PYROVEN_AAUTH = ''
```

The details of these can be found in the Raven WLS protocol documentation, [here](http://raven.cam.ac.uk/project/waa2wls-protocol.txt).
