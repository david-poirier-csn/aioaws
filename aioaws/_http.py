import asyncio
import gzip

import response

async def request(req):
    req.headers['User-Agent'] = 'aioaws/1'
    req.headers['Accept-Encoding'] = 'gzip'
    if req.body and 'Content-Length' not in req.headers:
        req.headers['Content-Length'] = str(len(req._get_body_bytes()))

    reader, writer = await asyncio.open_connection(
            req.headers['Host'], 443, ssl=True)
    
    await _write_data(writer, req._get_head_bytes())
    if req.body:
        await _write_data(writer, req._get_body_bytes())

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
        resp._set_body(await _read_data(reader, resp.content_length()))
    elif resp.transfer_encoding() == 'chunked':
        resp._set_body(await _read_chunked_response(reader))

    if resp.content_encoding() == 'gzip':
        resp._set_body(gzip.decompress(resp.body))

    writer.close()

    return resp


async def _write_data(writer, data):
    max_write_size = 1024 * 16
    bytes_written = 0
    while bytes_written < len(data):
        bytes_left = len(data) - bytes_written
        write_size = min(bytes_left, max_write_size)
        writer.write(data[bytes_written:bytes_written+write_size])
        await writer.drain()
        bytes_written += write_size

async def _read_data(reader, data_length):
    max_read_size = 1024 * 16
    bytes_read = 0
    data = b''
    while bytes_read < data_length:
        bytes_left = data_length - bytes_read
        read_size = min(bytes_left, max_read_size)
        d = await reader.read(read_size) 
        bytes_read += len(d)
        data += d
    return data


async def _read_chunked_response(reader):
    data = b''
    while True:
        line = await reader.readline()
        data_length = int(line.strip(), 16)
        if data_length == 0:
            # consume trailing blank line and exit
            await reader.readline()
            break
        else:
            data += await _read_data(reader, data_length)
            # consume trailing line break
            await _read_data(reader, 2)
    return data

