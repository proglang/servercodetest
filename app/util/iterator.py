import re


def lines(data: str):
    return iterate(data, r"[^\n]+")


def iterate(data: str, regex: str):
    return (x.group(0).strip("") for x in re.finditer(regex, data.strip()))
