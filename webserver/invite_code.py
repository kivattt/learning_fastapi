import random

invite_code_length: int = 24


def generate_invite_code():
    return random.randbytes(invite_code_length // 2).hex()


# Returns true if `s` is a (case-insensitive) hex string of length 24
def is_invite_code(s: str) -> bool:
    if len(s) != invite_code_length:
        return False

    for c in s:
        if c not in "0123456789abcdefABCDEF":
            return False

    return True
