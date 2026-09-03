import re


UGANDA_MOBILE_PATTERN = (
    r"^2567\d{8}$"
)


def validate_uganda_phone_number(
    phone_number,
):
    phone_number = (
        str(phone_number)
        .strip()
    )

    if not re.fullmatch(
        UGANDA_MOBILE_PATTERN,
        phone_number,
    ):
        raise ValueError(
            "Enter a valid Ugandan mobile "
            "number using the "
            "256XXXXXXXXX format."
        )

    return phone_number