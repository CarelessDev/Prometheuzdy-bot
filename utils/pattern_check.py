import re

def phone_check(string: str):
    pattern = r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$"

    if re.match(pattern, string):
        result = re.search(pattern, string)
        return "-".join(result.groups()[1:4])
    else:
        return False