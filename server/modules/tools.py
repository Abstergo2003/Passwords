from flask import make_response, Response
from flask_bcrypt import Bcrypt

# Inicjalizujemy obiekt, ale jeszcze bez aplikacji
bcrypt = Bcrypt()


# def obfuscateString(input, percentage):
#     startIndex = int((100 - percentage) / 100 * len(input))
#     endIndex = len(input) - startIndex
#     prefix = input[0:startIndex]
#     endfix = input[endIndex : len(input)]
#     return prefix + "****" + endfix


def generateUnauthorized() -> Response:
    """Generates response for 401 error

    Returns:
        Response: 401 error response
    """
    response = make_response(
        {"error": "Unauthorized"},
        401,
    )
    return response
