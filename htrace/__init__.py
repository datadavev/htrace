import logging
import re
import requests
import datetime
import dateparser

USER_AGENT = "htrace-0.1.0/python-3.9"

ACCEPT_VALUES = {
    "jld": "application/ld+json",
    "jsonld": "application/ld+json",
    "json-ld": "application/ld+json",
}

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
        # from time.time(), which is offset from epoch UTC
        dt = datetime.datetime.fromtimestamp(V)
        #dt = dt.replace(tzinfo=datetime.timezone.utc)
        if assume_local:
            dt = dt.astimezone()
        else:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt
        #return utcFromDateTime(
        #    datetime.datetime.fromtimestamp(V), assume_local=assume_local
        #)
    if isinstance(V, str):
        return utcFromDateTime(
            dateparser.parse(V, settings={"RETURN_AS_TIMEZONE_AWARE": True}),
            assume_local=assume_local,
        )
    return None

def dtdsecs(t):
    return t.seconds + t.microseconds / 1000000.0

def responseSummary(resp, tstart, tend):
    """
    JSON-able conversion of requests response info dict

    Args:
        resp: A requests response-like thing

    Returns:
        dict

    """

    def httpDateToJson(d):
        if d is None:
            return d
        dt = datetimeFromSomething(d)
        return datetimeToJsonStr(dt)

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

        loc = r.headers.get("Location", None)
        if loc is not None:
            row["result"] = f"Location: {loc}"
        else:
            row["result"] = "<< body >>"
        return row

    elapsed = 0.0
    rs = {
        "request": {},
        "responses": [],
        "resources_loaded": [],
        "tstart": datetimeToJsonStr(datetimeFromSomething(tstart, assume_local=False)),
        "tend": datetimeToJsonStr(datetimeFromSomething(tend, assume_local=False)),
        "elapsed": elapsed,
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
        elapsed += rs["responses"][-1]["elapsed"]
    rs["responses"].append(addHistory(resp))
    elapsed += rs["responses"][-1]["elapsed"]
    rs["elapsed"] = elapsed
    return rs

# FROM: https://github.com/digitalbazaar/pyld/blob/master/lib/pyld/jsonld.py L337
# With adjustment to always return lists
def parseLinkHeader(header):
    """
    Parses a link header. The results will be key'd by the value of "rel".
    Link: <http://json-ld.org/contexts/person.jsonld>; \
      rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"
    Parses as: {
      'http://www.w3.org/ns/json-ld#context': [
          {
            target: http://json-ld.org/contexts/person.jsonld, 
            type: 'application/ld+json'
          }
      ]
    }
    If there is more than one "rel" with the same IRI, then entries in the
    resulting map for that "rel" will be lists.
    :param header: the link header to parse.
    :return: the parsed result.
    """
    rval = {}
    # split on unbracketed/unquoted commas
    entries = re.findall(r'(?:<[^>]*?>|"[^"]*?"|[^,])+', header)
    if not entries:
        return rval
    r_link_header = r'\s*<([^>]*?)>\s*(?:;\s*(.*))?'
    for entry in entries:
        match = re.search(r_link_header, entry)
        if not match:
            continue
        match = match.groups()
        result = {'target': match[0]}
        params = match[1]
        r_params = r'(.*?)=(?:(?:"([^"]*?)")|([^"]*?))\s*(?:(?:;\s*)|$)'
        matches = re.findall(r_params, params)
        for match in matches:
            result[match[0]] = match[2] if match[1] is None else match[1]
        rel = result.get('rel', '')
        if isinstance(rval.get(rel), list):
            rval[rel].append(result)
        else:
            rval[rel] = [result,]
    return rval