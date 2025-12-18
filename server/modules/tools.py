from flask import make_response


def obfuscateString(input, percentage):
    startIndex = int((100 - percentage) / 100 * len(input))
    endIndex = len(input) - startIndex
    prefix = input[0:startIndex]
    endfix = input[endIndex : len(input)]
    return prefix + "****" + endfix


def generateUnauthorized():
    response = make_response(
        {"error": "Unauthorized"},
        401,
    )
    return response
