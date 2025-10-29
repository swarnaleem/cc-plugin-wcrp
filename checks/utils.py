import os
import re
from datetime import timedelta

import numpy as np
from compliance_checker.base import BaseCheck

try:
    from esgvoc.api.universe import find_terms_in_data_descriptor

    ESG_VOCAB_AVAILABLE = True
except ImportError:
    ESG_VOCAB_AVAILABLE = False


# === Map severity constants to textual qualifiers ===

SEVERITY_WORDING_MAP = {
    BaseCheck.HIGH: "required",
    BaseCheck.MEDIUM: "recommended",
    BaseCheck.LOW: "suggested",
}
SEVERITY_WORDING_MAP_NOUN = {
    BaseCheck.HIGH: "requirement",
    BaseCheck.MEDIUM: "recommendation",
    BaseCheck.LOW: "suggestion",
}


def severity_word(severity, noun=False):
    """
    Return a human-readable qualifier ("required", "recommended", "suggested")
    for a given severity constant or string.
    """
    if isinstance(severity, str):
        s = severity.upper()[0]
        if s == "H":
            if noun:
                return SEVERITY_WORDING_MAP_NOUN[BaseCheck.HIGH]
            return SEVERITY_WORDING_MAP[BaseCheck.HIGH]
        elif s == "M":
            if noun:
                return SEVERITY_WORDING_MAP_NOUN[BaseCheck.MEDIUM]
            return SEVERITY_WORDING_MAP[BaseCheck.MEDIUM]
        elif s == "L":
            if noun:
                return SEVERITY_WORDING_MAP_NOUN[BaseCheck.LOW]
            return SEVERITY_WORDING_MAP[BaseCheck.LOW]
    if noun:
        return SEVERITY_WORDING_MAP_NOUN.get(severity, "recommendation")
    return SEVERITY_WORDING_MAP.get(severity, "recommended")


# === Mapping CMOR<-->python datatypes
dtypesdict = {
    "integer": np.int32,
    "long": np.int64,
    "real": np.float32,
    "double": np.float64,
    "character": "S",
}
_dtypesdict = {
    **dtypesdict,
    "character": str,
}


# === cc_plugin_cc6 utils and constants ===


def convert_posix_to_python(posix_regex):
    """
    Convert common POSIX regular expressions to Python regular expressions.

    Args:
        posix_regex (str): The POSIX regular expression to convert.

    Returns:
        str: The converted Python regular expression.

    Raises:
        ValueError: If the input is not a string or contains invalid POSIX character classes.
    """
    if not isinstance(posix_regex, str):
        raise ValueError("Input must be a string")

    # Dictionary of POSIX to Python character class conversions
    posix_to_python_classes = {
        r"[[:alnum:]]": r"[a-zA-Z0-9]",
        r"[[:alpha:]]": r"[a-zA-Z]",
        r"[[:digit:]]": r"\d",
        r"[[:xdigit:]]": r"[0-9a-fA-F]",
        r"[[:lower:]]": r"[a-z]",
        r"[[:upper:]]": r"[A-Z]",
        r"[[:blank:]]": r"[ \t]",
        r"[[:space:]]": r"\s",
        r"[[:punct:]]": r'[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]',
        r"[[:word:]]": r"\w",
    }

    # Replace POSIX character classes with Python equivalents
    for posix_class, python_class in posix_to_python_classes.items():
        posix_regex = posix_regex.replace(posix_class, python_class)

    # Replace POSIX quantifiers with Python equivalents
    posix_regex = posix_regex.replace(r"\{", "{").replace(r"\}", "}")

    return posix_regex


def match_pattern_or_string(pattern, target):
    """
    Compare a regex pattern or a string with the target string.

    Args:
        pattern (str): The regex pattern or string to compare.
        target (str): The string to compare against.

    Returns:
        bool: True if the target matches the regex pattern or is equal to the string.
    """
    return bool(
        re.fullmatch(convert_posix_to_python(pattern), target, flags=re.ASCII)
    ) or (
        pattern == target
        and convert_posix_to_python(target) == target
        and ".*" not in target
    )


def to_str(val):
    """
    Decode byte strings to utf-8 if possible and leave other typed input unchanged.
    """
    if isinstance(val, (bytes, np.bytes_)):
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return val
    return str(val)


def printtimedelta(d):
    """Return timedelta (s) as either min, hours, days, whatever fits best."""
    if d > 86000:
        return f"{d/86400.} days"
    if d > 3500:
        return f"{d/3600.} hours"
    if d > 50:
        return f"{d/60.} minutes"
    else:
        return f"{d} seconds"


def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


# Definition of maximum deviations from the given frequency
deltdic = {}
deltdic["monmax"] = timedelta(days=31.5).total_seconds()
deltdic["monmin"] = timedelta(days=27.5).total_seconds()
deltdic["mon"] = timedelta(days=31).total_seconds()
deltdic["daymax"] = timedelta(days=1.1).total_seconds()
deltdic["daymin"] = timedelta(days=0.9).total_seconds()
deltdic["day"] = timedelta(days=1).total_seconds()
deltdic["1hrmin"] = timedelta(hours=0.9).total_seconds()
deltdic["1hrmax"] = timedelta(hours=1.1).total_seconds()
deltdic["1hr"] = timedelta(hours=1).total_seconds()
deltdic["3hrmin"] = timedelta(hours=2.9).total_seconds()
deltdic["3hrmax"] = timedelta(hours=3.1).total_seconds()
deltdic["3hr"] = timedelta(hours=3).total_seconds()
deltdic["6hrmin"] = timedelta(hours=5.9).total_seconds()
deltdic["6hrmax"] = timedelta(hours=6.1).total_seconds()
deltdic["6hr"] = timedelta(hours=6).total_seconds()
deltdic["yrmax"] = timedelta(days=366.1).total_seconds()
deltdic["yrmin"] = timedelta(days=359.9).total_seconds()
deltdic["yr"] = timedelta(days=360).total_seconds()
deltdic["subhr"] = timedelta(seconds=600).total_seconds()
deltdic["subhrmax"] = timedelta(seconds=601).total_seconds()
deltdic["subhrmin"] = timedelta(seconds=599).total_seconds()
deltdic["dec"] = timedelta(days=3600).total_seconds()
deltdic["decmax"] = timedelta(days=3599.99).total_seconds()
deltdic["decmin"] = timedelta(days=3660.01).total_seconds()
deltdic["cen"] = timedelta(days=36000).total_seconds()
deltdic["cenmax"] = timedelta(days=35999.99).total_seconds()
deltdic["cenmin"] = timedelta(days=36600.01).total_seconds()
# CMIP-style frequencies for "time: point":
for l_freq in ["subhr", "1hr", "3hr", "6hr", "day", "mon", "yr"]:
    deltdic[l_freq + "Pt"] = deltdic[l_freq]
    deltdic[l_freq + "Ptmax"] = deltdic[l_freq + "max"]
    deltdic[l_freq + "Ptmin"] = deltdic[l_freq + "min"]


def retrieve(url, fname, path, force=False):
    """
    Retrieve a file from a given URL and save it to a local path.
    """
    import pooch

    # Create the full path to the file
    full_path = os.path.join(os.path.expanduser(path), fname)
    # Check if the file exists locally and delete if redownload is forced
    if os.path.isfile(full_path) and force:
        print(f"Removing existing file '{full_path}'")
        os.remove(full_path)

    filename = pooch.retrieve(
        url=url,
        fname=fname,
        known_hash=None,
        path=path,
    )
    return filename
