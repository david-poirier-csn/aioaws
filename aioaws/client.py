import asyncio


async def request(req):
    reader, writer = await asyncio.open_connection(
            req.headers['Host'], 443, ssl=True)
    
    writer.write(req._get_head_bytes())
    #await writer.drain()

    if req.body:
        writer.write(req.body)
        await writer.drain()

    resp_header = []
    while True:
        head = await reader.readline()
        head = head.decode('utf-8')
        if head=='\r\n' or head is None:
            break
        resp_header.append(head)

    version, status_code, reason = _parse_status_line(resp_header[0])
    print(version, status_code, reason)

    headers = _parse_headers(resp_header[1:])
    print(headers)

    while True:
        data = await reader.readline()
        if data is None:
            break
        print(data)

    writer.close()


def _parse_status_line(status_line):
    parts = status_line.strip().split(' ')
    version = parts[0]
    status_code = parts[1]
    reason = ' '.join(parts[2:])
    return version, status_code, reason


def _parse_headers(header_lines):
    headers = {}
    for l in header_lines:
        sep = l.find(':')
        k = l[:sep]
        v = l[sep+1:]
        headers[k.strip()] = v.strip()
    return headers

