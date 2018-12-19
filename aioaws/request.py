import json

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
        head = f'{self.method} {self.url} {self.version}\r\n'
        for k in self.headers:
            v = self.headers[k]
            head += f'{k}:{v}\r\n'
        head += '\r\n'
        return head


    def _get_head_bytes(self):
        return self._get_head_text().encode('utf-8')


    def _get_body_text(self):
        if self.body is None:
            return None

        if isinstance(self.body, str):
            return self.body
        elif isinstance(self.body, dict):
            return json.dumps(self.body)
        else:
            return str(self.body)
    
    
    def _get_body_bytes(self):
       if isinstance(self.body, bytes):
           return self.body
       else:
           text = self._get_body_text()
           if text is None:
               return None
           return text.encode('utf-8')

