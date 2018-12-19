import _http, signer

async def request(request, region, service, credentials):
    signed_request = signer.sign_request(request, region, service, credentials)
    response = await _http.request(signed_request)
    return response

