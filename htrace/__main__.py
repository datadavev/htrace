import sys
import logging
import click
import htrace
import requests
import json
import time
import urllib.parse
import urllib3

W = "\033[0m"  # white (normal)
R = "\033[31m"  # red
G = "\033[32m"  # green
O = "\033[33m"  # orange
B = "\033[34m"  # blue
P = "\033[35m"  # purple

# Global for access by event hooks
session = requests.Session()


def printSummary(s):
    L = logging.getLogger("SUMMARY:")
    L.info(f"Start URL: {s['responses'][0]['url']}")
    L.info(f"Final URL: {s['request']['url']}")
    L.info(f"Start: {s['tstart']}")
    L.info(f"Num requests: {len(s['responses'])}")
    L.info(f"Elapsed: {s['elapsed']:.3f} seconds")


def cbUrl(response, *args, **kwargs):
    OUT = logging.getLogger(">")
    IN = logging.getLogger("<")
    OUT.info(f"{G}{response.request.method}: {response.request.url}{W}")
    OUT.info(f"{G}Accept: {response.request.headers.get('Accept', '-')}{W}")
    IN.info(f"{P}{response.status_code}{B} {response.url}{W}")
    rh = response.headers
    for h in sorted(response.headers.keys()):
        IN.info(f"{B}{h}{W}: {response.headers[h]}")
    IN.info(f"{R}{htrace.dtdsecs(response.elapsed):.4f} sec{W}")


def cbUrlMinimum(response, *args, **kwargs):
    OUT = logging.getLogger(">")
    IN = logging.getLogger("<")
    OUT.info(f"{G}{response.request.method}: {response.request.url}{W}")
    meta = (
        response.headers.get("location", response.headers.get("content-type"))
        .encode("iso-8859-1")
        .decode()
    )
    IN.info(f"{P}{response.status_code}{B} {G}{meta}{W}")
    IN.info(f"{R}{htrace.dtdsecs(response.elapsed):.4f} sec{W}")


def cbLinkFollow(response, *args, **kwargs):
    global session
    L = logging.getLogger("L")
    # First check to see if response matches requested properties
    if session._extra["link_type"] is not None:
        if (
            response.headers.get("Content-Type", "").find(session._extra["link_type"])
            >= 0
        ):
            if session._extra["link_profile"] is None:
                L.info(f"Match linked type {R}{session._extra['link_type']}{W}")
                return
            _profile = response.headers.get("Content-Profile", "")
            if _profile.find(session._extra["link_profile"]) >= 0:
                L.info(
                    f"Match linked type {R}{session._extra['link_type']}{W} and profile {R}{session._extra['link_profile']}{W}"
                )
                return

    alllinks = htrace.parseLinkHeader(response.headers.get("Link", ""))
    lhs = alllinks.get(session._extra["link_rel"], [])
    for lh in lhs:
        if lh["type"] == session._extra["link_type"]:
            if (
                session._extra["link_profile"] is None
                or lh.get("profile", "") == session._extra["link_profile"]
            ):
                link_url = urllib.parse.urljoin(response.url, lh["target"])
                # Fake out requests with an injected redirect
                response.headers["Location"] = lh["target"]
                response.status_code = 302
                L.info(f"Follow Link: {R}{link_url}{W}")
                return response


@click.command()
@click.version_option()
@click.argument("url")
@click.option("-T", "--timeout", default=10, help="Request timeout in seconds")
@click.option("-a", "--accept", default="*/*", help="Accept header value")
@click.option("-b", "--body", is_flag=True, help="Show response body")
@click.option("-j", "--json", "json_report", is_flag=True, help="Report in JSON")
@click.option(
    "-k", "--insecure", default=False, is_flag=True, help="Don't verify certificates"
)
@click.option("-L", "--link-type", default=None, help="Follow link header with type")
@click.option(
    "-P", "--link-profile", default=None, help="Follow link header with profile"
)
@click.option(
    "-R", "--link-rel", default="alternate", help="Follow link header with rel"
)
@click.option("-U", "--user-agent", default=None, help="User agent header value")
@click.option("-m", "--minimal", is_flag=True, help="Minimal redirect info")
@click.option("--log_time", is_flag=True, help="Show timestamp in output")
def main(
    url,
    timeout,
    accept,
    body,
    json_report,
    insecure,
    link_type,
    link_profile,
    link_rel,
    user_agent,
    minimal,
    log_time,
):
    if insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    lformat = "%(name)s %(message)s"
    if log_time:
        lformat = "%(asctime)s.%(msecs)03d:%(name)s %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=lformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    accept = htrace.ACCEPT_VALUES.get(accept, accept)
    global session
    headers = {
        "Accept": accept,
        "User-Agent": htrace.USER_AGENT,
    }
    if not user_agent is None:
        headers["User-Agent"] = user_agent
    # https://docs.python-requests.org/en/master/user/advanced/#event-hooks
    url_cb = cbUrl
    if minimal:
        url_cb = cbUrlMinimum
    hooks = {"response": [url_cb, cbLinkFollow]}
    tstart = time.time()
    session._extra = {
        "link_type": link_type,
        "link_rel": link_rel,
        "link_profile": link_profile,
    }
    response = session.get(
        url,
        timeout=timeout,
        headers=headers,
        hooks=hooks,
        allow_redirects=True,
        verify=not insecure,
    )
    tend = time.time()
    summary = htrace.responseSummary(response, tstart, tend)
    if json_report:
        sys.stderr.write(json.dumps(summary, indent=2))
        if body:
            print(response.text)
        return 0
    printSummary(summary)
    if body:
        print(response.text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
