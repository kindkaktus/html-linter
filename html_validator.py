#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import gzip
import json

# Tackle python 2 and 3 differences
try:
    import httplib
except ImportError:
    import http.client as httplib

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO


def _prepare_request(url, service):
    url = service + '?doc=' + url + '&out=json&level=error'
    return url


def _make_request(url):
    connection = None
    response = None
    status = 302
    redirect_count = 0

    while status in (302, 301, 307) and redirect_count < 5:
        if redirect_count > 0:
            url = response.getheader('Location')
        parsed = urlparse.urlsplit(url)

        if redirect_count > 0:
            connection.close()

        if parsed.scheme == 'https':
            connection = httplib.HTTPSConnection(parsed[1])
        else:
            connection = httplib.HTTPConnection(parsed[1])

        headers = {
            'user-agent': 'HTML Validator'
        }
        url_suffix = '%s?%s' % (parsed[2], parsed[3])

        connection.connect()
        connection.request('GET', url_suffix, headers=headers)

        response = connection.getresponse()
        status = response.status

        redirect_count += 1

    return (response, status, connection)


def _parse_response(response, status, connection, error_ignore_regex):
    if status != 200:
        raise Exception('error %s %s' % (status, response.reason))

    if response.getheader('Content-Encoding', 'identity').lower() == 'gzip':
        response = gzip.GzipFile(fileobj=BytesIO(response.read()))

    output = response.read()
    if not isinstance(output, str):
        output = output.decode('utf-8')

    connection.close()

    json_output = json.loads(output)
    errors = [message for message in json_output['messages'] if message['type'] == u'error']

    # filter out errors a user does not consider as errors
    if error_ignore_regex:
        errors = [error for error in errors if not error_ignore_regex.match(error['message'])]

    # format errors a bit
    errors = [u"Error on line {0}:{1}. {2}. HTML code: {3}".format(
        error['firstLine'] if 'firstLine' in error else error['lastLine'],
        error['firstColumn'] if 'firstColumn' in error else error['lastColumn'],
        error['message'],
        error['extract']) for error in errors]

    return errors


# alternative URLs:
# https://checker.html5.org/
# https://validator.w3.org/nu/
# https://html5.validator.nu/
# see https://github.com/validator/validator for more info
def validate(url, service='https://checker.html5.org/', error_ignore_regex=None):
    """ return error list """
    request_url = _prepare_request(url, service)
    (response, status, connection) = _make_request(request_url)
    result = _parse_response(response, status, connection, error_ignore_regex)
    return result
