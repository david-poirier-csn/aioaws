import asyncio

import response

async def request(req):
    if 'User-Agent' not in req.headers:
        req.headers['User-Agent'] = 'aioaws/1'
    if req.body and 'Content-Length' not in req.headers:
        req.headers['Content-Length'] = str(len(req._get_body_bytes()))

    reader, writer = await asyncio.open_connection(
            req.headers['Host'], 443, ssl=True)
    
    writer.write(req._get_head_bytes())
    await writer.drain()

    if req.body:
        writer.write(req._get_body_bytes())
        await writer.drain()

    resp_header = []
    while True:
        head = await reader.readline()
        head = head.decode('utf-8')
        if head=='\r\n' or head is None:
            break
        resp_header.append(head)

    resp = response.Response()
    resp._parse_status_line(resp_header[0])
    resp._parse_headers(resp_header[1:])

    if resp.content_length() > 0:
        body = await reader.read(resp.content_length())
        resp._set_body(body)
    elif resp.transfer_encoding() == 'chunked':
        body = b''
        while True:
            line = await reader.readline()
            if line == b'':
                break
            body += line
        resp._set_body(body)

    writer.close()

    return resp

