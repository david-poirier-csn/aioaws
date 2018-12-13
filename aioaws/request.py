class Request:
    def __init__(self, *,
            method,
            url,
            headers,
            body=None):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def _get_head_bytes(self):
        head = f'{self.method} {self.url} HTTP/1.1\r\n'
        for k in self.headers:
            head += f'{k}:{self.headers[k]}\r\n'
        head += '\r\n'
        return head.encode('utf-8')

