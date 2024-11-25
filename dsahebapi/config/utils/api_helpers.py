from typing import Any, Dict, Optional

def create_response(status: str, message: str, data: Optional[Any] = None) -> Dict:
    """
    Creates a standardized API response body.

    Args:
        status (str): The status of the request, either 'success' or 'failure'.
        message (str): A message describing the result.
        data (Any, optional): The response data (if any). Defaults to None.

    Returns:
        dict: A standardized response dictionary.
    """
    return {
        "status": status,
        "message": message,
        "data": data if data is not None else None
    }


def success_response(message: str, data: Optional[Any] = None) -> Dict:
    """
    Creates a success response body.

    Args:
        message (str): The success message.
        data (Any, optional): The response data. Defaults to None.

    Returns:
        dict: A success response.
    """
    return create_response(status="success", message=message, data=data)


def failure_response(message: str, data: Optional[Any] = None) -> Dict:
    """
    Creates a failure response body.

    Args:
        message (str): The failure message.
        data (Any, optional): The failure data. Defaults to None.

    Returns:
        dict: A failure response.
    """
    return create_response(status="failure", message=message, data=data)


def error_response(message: str, data: Optional[Any] = None) -> Dict:
    """
    Creates an error response body.

    Args:
        message (str): The error message.
        data (Any, optional): The error data. Defaults to None.

    Returns:
        dict: An error response.
    """
    return create_response(status="error", message=message, data=data)

COMMON_HEADERS = {
    "Content-Type": "application/json",
    "X-Powered-By": "Django-Ninja API"
}

def add_common_headers(response_data: Dict) -> Dict:
    """
    Adds common headers to the API response.

    Args:
        response_data (dict): The API response data.

    Returns:
        dict: The response data with added headers.
    """
    headers = COMMON_HEADERS
    return headers
