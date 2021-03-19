# htrace

Simple command line utility for tracing HTTP requests over redirects.

```
Usage: htrace [OPTIONS] URL

Options:
  -T, --timeout INTEGER  Request timeout in seconds
  -a, --accept TEXT      Accept header value
  -j, --json             Report in JSON
  -b, --body             Show response body
  --help                 Show this message and exit.
```

Example:
```
% htrace "http://schema.org/"
2021-03-19 08:18:09.371:> GET: http://schema.org/
2021-03-19 08:18:09.371:> Accept: */*
2021-03-19 08:18:09.371:< 301 http://schema.org/
2021-03-19 08:18:09.371:< Content-Length: 0
2021-03-19 08:18:09.371:< Content-Type: text/html
2021-03-19 08:18:09.371:< Date: Fri, 19 Mar 2021 12:18:09 GMT
2021-03-19 08:18:09.371:< Location: https://schema.org/
2021-03-19 08:18:09.371:< Server: Google Frontend
2021-03-19 08:18:09.371:< X-Cloud-Trace-Context: dc661d58e457af35212814c8e90163f8
2021-03-19 08:18:09.371:< 0.0603 sec
2021-03-19 08:18:09.426:> GET: https://schema.org/
2021-03-19 08:18:09.426:> Accept: */*
2021-03-19 08:18:09.426:< 200 https://schema.org/
2021-03-19 08:18:09.426:< Access-Control-Allow-Credentials: true
2021-03-19 08:18:09.426:< Access-Control-Allow-Headers: Accept
2021-03-19 08:18:09.426:< Access-Control-Allow-Methods: GET
2021-03-19 08:18:09.426:< Access-Control-Allow-Origin: *
2021-03-19 08:18:09.426:< Access-Control-Expose-Headers: Link
2021-03-19 08:18:09.426:< Age: 413
2021-03-19 08:18:09.426:< Alt-Svc: h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
2021-03-19 08:18:09.426:< Cache-Control: public, max-age=600
2021-03-19 08:18:09.426:< Content-Encoding: gzip
2021-03-19 08:18:09.426:< Content-Length: 2206
2021-03-19 08:18:09.426:< Content-Type: text/html
2021-03-19 08:18:09.426:< Date: Fri, 19 Mar 2021 12:11:16 GMT
2021-03-19 08:18:09.426:< ETag: "z2afww"
2021-03-19 08:18:09.427:< Expires: Fri, 19 Mar 2021 12:21:16 GMT
2021-03-19 08:18:09.427:< Link: </docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"
2021-03-19 08:18:09.427:< Server: Google Frontend
2021-03-19 08:18:09.427:< X-Cloud-Trace-Context: 63d878a82afe363fca6c584963eb764b
2021-03-19 08:18:09.427:< 0.0524 sec
2021-03-19 08:18:09.457:SUMMARY: Start URL: http://schema.org/
2021-03-19 08:18:09.457:SUMMARY: Final URL: https://schema.org/
2021-03-19 08:18:09.457:SUMMARY: Start: 2021-03-19T12:18:09+0000
2021-03-19 08:18:09.457:SUMMARY: Num requests: 2
2021-03-19 08:18:09.457:SUMMARY: Elapsed: 0.113 seconds
```
