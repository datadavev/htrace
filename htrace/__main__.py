import sys
import logging
import click
import htrace
import requests
import json
import time

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple

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

@click.command()
@click.argument("url")
@click.option("-T", "--timeout", default=10, help="Request timeout in seconds")
@click.option("-a", "--accept", default="*/*", help="Accept header value")
@click.option("-j", "--json", "json_report", is_flag=True, help="Report in JSON")
@click.option("-b", "--body", is_flag=True, help="Show response body")
def main(url, timeout, accept, json_report, body):
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s.%(msecs)03d:%(name)s %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S')
    accept = htrace.ACCEPT_VALUES.get(accept, accept)
    headers = {
        "Accept": accept,
        "User-Agent": htrace.USER_AGENT,
    }
    hooks = {
        'response': cbUrl,        
    }
    tstart = time.time()
    response = requests.get(url, timeout=timeout, headers=headers, hooks=hooks)
    tend = time.time()
    summary = htrace.responseSummary(response, tstart, tend)
    if json_report:
        sys.stderr.write(json.dumps(summary, indent=2))
        if body:
            print(respons.text)
        return 0
    printSummary(summary)
    if body:
        print(response.text)
    return 0

if __name__ == "__main__":
    sys.exit(main())