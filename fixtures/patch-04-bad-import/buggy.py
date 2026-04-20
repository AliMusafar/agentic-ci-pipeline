# This module directly imports internal implementation details
# instead of going through the public API.

# Wrong: imports private internals
from auth._internal.token_validator import validate_token_raw
from auth._internal.session_store import _get_session_by_id

# Should instead use:
# from auth import validate_token, get_session


def check_request(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not validate_token_raw(token):
        return None
    session_id = token.split(".")[1]
    return _get_session_by_id(session_id)
