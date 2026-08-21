import re


def validate_uganda_phone_number(phone_number):

    phone_number = phone_number.strip()

    pattern = r"^2567\d{8}$"

    if not re.match(pattern, phone_number):
        raise ValueError(
            "Enter a valid Ugandan mobile number "
            "using the 256XXXXXXXXX format."
        )

    return phone_number

def validate_uganda_phone_number(phone_number):

    phone_number = phone_number.strip()

    pattern = r"^2567\d{8}$"

    if not re.match(pattern, phone_number):
        raise ValueError(
            "Enter a valid Ugandan mobile number "
            "using the 256XXXXXXXXX format."
        )

    return phone_number