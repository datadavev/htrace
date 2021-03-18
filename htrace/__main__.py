import logging
import click
import htrace
import requests
import json

USER_AGENT = "htrace-0.1.0/python-3.9"

ACCEPT_VALUES = {
    "jld": "application/ld+json",
    "jsonld": "application/ld+json",
    "json-ld": "application/ld+json",
}

@click.command()
@click.argument("url")
@click.option("-T", "--timeout", default=10, help="Request timeout in seconds")
@click.option("-a", "--accept", default="*/*", help="Accept header value")
def main(url, timeout, accept):
    accept = ACCEPT_VALUES.get(accept, accept)
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
    }
    tstart = htrace.dtnow()
    response = requests.get(url, timeout=timeout, headers=headers)
    tend = htrace.dtnow()
    summary = htrace.responseSummary(response, tstart, tend)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()