import datetime
import hashlib
import hmac
import urllib.parse


def sign_request(
        request, region, service, credentials,
        *, include_security_token_in_signature=True):
    if 'X-Amz-Date' in request.headers:
        amzdate = request.headers['X-Amz-Date'][0]
    else:
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        request.headers['X-Amz-Date'] = [amzdate]
    datestamp = amzdate[:8]

    if credentials.token is not None and \
            'X-Amz-Security-Token' not in request.headers and \
            include_security_token_in_signature:
                request.headers['X-Amz-Security-Token'] = [credentials.token]

    url_parts = urllib.parse.urlsplit('https://' + request.url, allow_fragments=False)
    query = urllib.parse.parse_qs(url_parts.query, keep_blank_values=True)
    canonical_request = _create_canonical_request(
            request.method,
            url_parts.path,
            query,
            request.headers,
            request.body)
    string_to_sign = _create_string_to_sign(
            amzdate, datestamp, region, service, canonical_request)
    authorization_header = _create_authorization_header(
            credentials.key, credentials.secret, datestamp, 
            region, service, request.headers, string_to_sign)
    
    if credentials.token is not None and \
            'X-Amz-Security-Token' not in request.headers:
                request.headers['X-Amz-Security-Token'] = [credentials.token]
    request.headers['Authorization'] = [authorization_header]
    return request


def _create_canonical_request(method, path, query, headers, body):
    can_req = method + '\n'
    can_req += _create_canonical_path(path) + '\n'
    can_req += _create_canonical_query(query) + '\n'
    can_req += _create_canonical_headers(headers) + '\n'
    can_req += _create_signed_headers(headers) + '\n'
    can_req += _create_payload_hash(body)
    return can_req


def _create_canonical_path(path):
    can_path = path
    if can_path=='':
        can_path='/'
    while '//' in can_path:
        can_path = can_path.replace('//', '/')
    can_path = _resolve_path(can_path)
    while True:
        decoded_can_path = urllib.parse.unquote(can_path)
        if decoded_can_path != can_path:
            can_path = decoded_can_path
        else:
            break
    can_path = urllib.parse.quote(can_path.encode('utf-8'), safe='/~')
    return can_path


def _create_canonical_query(query):
    can_query = ''
    for k in sorted(query.keys()):
        for v in sorted(query[k]):
            if can_query != '':
                can_query += '&'
            k = urllib.parse.quote(k.encode('utf-8'))
            v = urllib.parse.quote(v.encode('utf-8'))
            can_query += k + '=' + v
    return can_query


def _create_canonical_headers(headers):
    can_headers = ''
    lower_headers = {}
    for k in headers.keys():
        if k not in lower_headers:
            lower_headers[k.lower()] = []
        lower_headers[k.lower()].append(headers[k])
    for k in sorted(lower_headers.keys()):
        can_headers += k + ':'
        values = []
        for vv in sorted(lower_headers[k]):
            for v in vv:
                if v.startswith('"') and v.endswith('"'):
                    while '  ' in v:
                        v = v.replace('  ', ' ')
                elif '\n' in v:
                    v = v.replace('\n', ' ')
                    while '  ' in v:
                        v = v.replace('  ', ' ')
                    v = v.replace(' ', ',')
                values.append(v)
        can_headers += ','.join(values) + '\n'
    return can_headers


def _create_signed_headers(headers):
    signed_headers = ''
    lower_headers = {}
    for k in headers.keys():
        if k.lower() not in lower_headers:
            lower_headers[k.lower()] = 'x'
    for k in sorted(lower_headers.keys()):
        if signed_headers != '':
            signed_headers += ';'
        signed_headers += k.lower()
    return signed_headers


def _create_payload_hash(body):
    if body is None:
        body = ''
    if isinstance(body, str):
        body = body.encode('utf-8')
    payload_hash = hashlib.sha256(body).hexdigest()
    return payload_hash


def _resolve_path(path):
    segments = path.split('/')
    segments = [segment + '/' for segment in segments[:-1]] + [segments[-1]]
    resolved = []
    for segment in segments:
        if segment in ('../', '..'):
            if resolved[1:]:
                resolved.pop()
        elif segment not in ('./', '.'):
            resolved.append(segment)
    path = ''.join(resolved)
    return path


def _create_string_to_sign(amzdate, datestamp, region, service, canonical_request):
    sts = 'AWS4-HMAC-SHA256\n'
    sts += amzdate + '\n'
    sts += datestamp + '/' + region + '/' + service + '/aws4_request\n'
    sts += hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    return sts


def _create_authorization_header(key, secret, datestamp, region, service, headers, string_to_sign):
    signing_key = hmac.new(f'AWS4{secret}'.encode('utf-8'), datestamp.encode('utf-8'), hashlib.sha256).digest()
    signing_key = hmac.new(signing_key, region.encode('utf-8'), hashlib.sha256).digest()
    signing_key = hmac.new(signing_key, service.encode('utf-8'), hashlib.sha256).digest()
    signing_key = hmac.new(signing_key, 'aws4_request'.encode('utf-8'), hashlib.sha256).digest()
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    auth_header = 'AWS4-HMAC-SHA256 '
    auth_header += 'Credential=' + key + '/' + datestamp + '/' + region + '/' + service + '/aws4_request, '
    auth_header += 'SignedHeaders=' + _create_signed_headers(headers) + ', '
    auth_header += 'Signature=' + signature
    return auth_header


__all__ = ['Signer']

