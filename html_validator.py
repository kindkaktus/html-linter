#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import gzip

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


def _prepare_request(url, errors_only, service):
    url = service + '?doc=' + url + '&out=text'
    if errors_only:
        url = url + '&level=error'
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
            'Content-Type': 'text/html'
        }
        url_suffix = '%s?%s' % (parsed[2], parsed[3])

        connection.connect()
        connection.request('GET', url_suffix, headers=headers)

        response = connection.getresponse()
        status = response.status

        redirect_count += 1

    return (response, status, connection)


def _parse_response(response, status, connection):
    if status != 200:
        raise Exception('error %s %s' % (status, response.reason))

    if response.getheader('Content-Encoding', 'identity').lower() == 'gzip':
        response = gzip.GzipFile(fileobj=BytesIO(response.read()))

    output = response.read()
    if not isinstance(output, str):
        output = output.decode('utf-8')

    connection.close()

    if output.find('There were errors.') != -1:
        return {'status': False, 'error': output}
    else:
        return {'status': True}


# return { status: flag
#        [, error : error-msg ] }
def validate(url, errors_only=False, service='https://html5.validator.nu/'):

    request_url = _prepare_request(url, errors_only, service)
    (response, status, connection) = _make_request(request_url)
    result = _parse_response(response, status, connection)

    return result
