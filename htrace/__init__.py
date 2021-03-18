import logging
import requests
import datetime
import dateparser

JSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""datetime format string for generating JSON content
"""

def getLogger():
    return logging.getLogger("htrace")

def datetimeToJsonStr(dt):
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Naive timestamp, convention is this must be UTC
        return f"{dt.strftime(JSON_TIME_FORMAT)}Z"
    return dt.strftime(JSON_TIME_FORMAT)


def dtnow():
    """
    Get datetime for now in UTC timezone.

    Returns:
        datetime.datetime with UTC timezone

    Example:

        .. jupyter-execute::

           import igsn_lib.time
           print(igsn_lib.time.dtnow())
    """
    return datetime.datetime.now(datetime.timezone.utc)


def utcFromDateTime(dt, assume_local=True):
    # is dt timezone aware?
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        if assume_local:
            # convert local time to tz aware utc
            dt.astimezone(datetime.timezone.utc)
        else:
            # asume dt is in UTC, add timezone
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    # convert to utc timezone
    return dt.astimezone(datetime.timezone.utc)


def datetimeFromSomething(V, assume_local=True):
    if V is None:
        return None
    if isinstance(V, datetime.datetime):
        return utcFromDateTime(V, assume_local=assume_local)
    if isinstance(V, float) or isinstance(V, int):
        return utcFromDateTime(
            datetime.datetime.fromtimestamp(V), assume_local=assume_local
        )
    if isinstance(V, str):
        return utcFromDateTime(
            dateparser.parse(V, settings={"RETURN_AS_TIMEZONE_AWARE": True}),
            assume_local=assume_local,
        )
    return None


def responseSummary(resp, tstart, tend):
    """
    JSON-able conversion of requests response info dict

    Args:
        resp: A requests response-like thing

    Returns:
        dict

    """

    def dtdsecs(t):
        return t.seconds + t.microseconds / 1000000.0

    def httpDateToJson(d):
        if d is None:
            return d
        dt = datetimeFromSomething(d)
        return datetimeToJsonStr(dt)

    elapsed = 0.0

    def addHistory(r):
        row = {
            "url": r.url,
            "status_code": r.status_code,
            "result": None,
            "elapsed": dtdsecs(r.elapsed),
            "headers": {},
        }
        for k in r.headers:
            row["headers"][k.lower()] = r.headers.get(k)

        row["content_type"] = row["headers"].get("content-type", None)
        row["last_modified"] = httpDateToJson(row["headers"].get("last-modified", None))
        row["date"] = httpDateToJson(row["headers"].get("date", None))

        nonlocal elapsed
        elapsed += dtdsecs(r.elapsed)

        loc = r.headers.get("Location", None)
        if loc is not None:
            row["result"] = f"Location: {loc}"
        else:
            row["result"] = "<< body >>"
        return row

    rs = {
        "request": {},
        "responses": [],
        "resources_loaded": [],
        "tstart": datetimeToJsonStr(tstart),
        "tend": datetimeToJsonStr(tend)
    }
    try:
        rs["resources_loaded"] = resp.resources_loaded
    except AttributeError as e:
        pass
    rs["request"]["url"] = resp.request.url
    rs["request"]["headers"] = {}
    for k in resp.request.headers:
        rs["request"]["headers"][k] = resp.request.headers.get(k)
    for r in resp.history:
        rs["responses"].append(addHistory(r))
    rs["responses"].append(addHistory(resp))
    return rs
