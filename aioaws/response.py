import json

class Response:
    def __init__(self):
        self.version=None
        self.status_code=None
        self.reason=None
        self.headers=None
        self.body=None

    def _parse_status_line(self, status_line):
        parts = status_line.strip().split(' ')
        self.version = parts[0]
        self.status_code = int(parts[1])
        self.reason = ' '.join(parts[2:])

    def _parse_headers(self, header_lines):
        self.headers = {}
        for l in header_lines:
            sep = l.find(':')
            k = l[:sep]
            v = l[sep+1:]
            self.headers[k.strip()] = v.strip()

    def _set_body(self, body):
        self.body = body

    def content_length(self):
        if 'Content-Length' in self.headers:
            return int(self.headers['Content-Length'])
        return 0

    def text(self):
        if self.body:
            return self.body.decode('utf-8')
        return None

    def json(self):
        if self.body:
            return json.loads(self.text())
        return None

