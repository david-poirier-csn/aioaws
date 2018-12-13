import hashlib
import hmac
import urllib

class Signer:
    def __init__(self):
        pass

    def _create_canonical_request(self, 
            method, path, query, headers, body):
        can_req = method + '\n'
        can_req += self._create_canonical_path(path) + '\n'
        can_req += self._create_canonical_query(query) + '\n'
        can_req += self._create_canonical_headers(headers) + '\n'
        can_req += self._create_signed_headers(headers) + '\n'
        can_req += self._create_payload_hash(body)
        return can_req

    def _create_canonical_path(self, path):
        can_path = path
        if can_path=='':
            can_path='/'
        can_path = self._resolve_path(can_path)
        can_path = urllib.parse.quote(can_path.encode('utf-8'), safe='/~')
        return can_path

    def _create_canonical_query(self, query):
        can_query = ''
        for k in sorted(query.keys()):
            for v in sorted(query[k]):
                if can_query != '':
                    can_query += '&'
                can_query += urllib.parse.quote(k.encode('utf-8'), safe='/~')
                can_query += '=' + urllib.parse.quote(v.encode('utf-8'), safe='/~')
        return can_query

    def _create_canonical_headers(self, headers):
        can_headers = ''
        for k in sorted(headers.keys()):
            v = headers[k]
            if v.startswith('"') and v.endswith('"'):
                while '  ' in v:
                    v = v.replace('  ', ' ')
            can_headers += k.lower() + ':' + v + '\n'
        return can_headers

    def _create_signed_headers(self, headers):
        signed_headers = ''
        for k in sorted(headers.keys()):
            if signed_headers != '':
                signed_headers += ';'
            signed_headers += k.lower()
        return signed_headers

    def _create_payload_hash(self, body):
        if isinstance(body, str):
            body = body.encode('utf-8')
        payload_hash = hashlib.sha256(body).hexdigest()
        return payload_hash

    def _resolve_path(self, path):
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

    def _create_string_to_sign(self, date, region, service, canonical_request):
        sts = 'AWS4-HMAC-SHA256\n'
        sts += date + '\n'
        sts += date[:8] + '/' + region + '/' + service + '/aws4_request\n'
        sts += hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        return sts

    def _create_authorization_header(self, key, secret, date, region, service, headers, string_to_sign):
        signing_key = hmac.new(f'AWS4{secret}'.encode('utf-8'), date[:8].encode('utf-8'), hashlib.sha256).digest()
        signing_key = hmac.new(signing_key, region.encode('utf-8'), hashlib.sha256).digest()
        signing_key = hmac.new(signing_key, service.encode('utf-8'), hashlib.sha256).digest()
        signing_key = hmac.new(signing_key, 'aws4_request'.encode('utf-8'), hashlib.sha256).digest()
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        auth_header = 'AWS4-HMAC-SHA256 '
        auth_header += 'Credential=' + key + '/' + date[:8] + '/' + region + '/' + service + '/aws4_request, '
        auth_header += 'SignedHeaders=' + self._create_signed_headers(headers) + ', '
        auth_header += 'Signature=' + signature
        return auth_header


__all__ = ['Signer']

