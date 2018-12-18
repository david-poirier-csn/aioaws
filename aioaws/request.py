class Request:
    def __init__(self, *,
            method,
            url,
            version,
            headers,
            body=None):
        self.method = method
        self.url = url
        self.version = version
        self.headers = headers
        self.body = body


    def _get_head_text(self):
        head = f'{self.method} {self.url} {self.version}\n'
        for k in self.headers:
            for v in self.headers[k]:
                head += f'{k}:{v}\n'
        head += '\r\n'
        return head

    def _get_head_bytes(self):
        return self._get_head_text().encode('utf-8')

