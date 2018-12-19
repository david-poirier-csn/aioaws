import asyncio

import response

async def request(req):
    reader, writer = await asyncio.open_connection(
            req.headers['Host'], 443, ssl=True)
    
    writer.write(req._get_head_bytes())
    await writer.drain()

    if req.body:
        if isinstance(req.body, str):
            writer.write(req.body.encode('utf-8'))
        else:
            writer.write(req.body)
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

    writer.close()

    return resp

