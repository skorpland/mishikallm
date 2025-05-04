from fastapi import Request


def get_mishikallm_virtual_key(request: Request) -> str:
    """
    Extract and format API key from request headers.
    Prioritizes x-mishikallm-api-key over Authorization header.


    Vertex JS SDK uses `Authorization` header, we use `x-mishikallm-api-key` to pass mishikallm virtual key

    """
    mishikallm_api_key = request.headers.get("x-mishikallm-api-key")
    if mishikallm_api_key:
        return f"Bearer {mishikallm_api_key}"
    return request.headers.get("Authorization", "")
