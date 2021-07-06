# htrace

Simple command line utility for tracing HTTP requests over redirects.

```
Usage: htrace [OPTIONS] URL

Options:
  -T, --timeout INTEGER    Request timeout in seconds
  -a, --accept TEXT        Accept header value
  -b, --body               Show response body
  -j, --json               Report in JSON
  -k, --insecure           Don't verify certificates
  -L, --link-type TEXT     Follow link header with type
  -P, --link-profile TEXT  Follow link header with profile
  -R, --link-rel TEXT      Follow link header with rel
  -U, --user-agent TEXT    User agent header value
  --help                   Show this message and exit.
  --version                Print version info
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

Example following link header:
```
% htrace "http://schema.org/" -L "application/ld+json" -b | more
2021-03-19 10:08:01.826:> GET: http://schema.org/
2021-03-19 10:08:01.826:> Accept: */*
2021-03-19 10:08:01.826:< 301 http://schema.org/
2021-03-19 10:08:01.826:< Content-Length: 0
2021-03-19 10:08:01.827:< Content-Type: text/html
2021-03-19 10:08:01.827:< Date: Fri, 19 Mar 2021 14:08:01 GMT
2021-03-19 10:08:01.827:< Location: https://schema.org/
2021-03-19 10:08:01.827:< Server: Google Frontend
2021-03-19 10:08:01.827:< X-Cloud-Trace-Context: fe909d0f5514086d3931cb6d1a64f764
2021-03-19 10:08:01.827:< 0.0623 sec
2021-03-19 10:08:01.892:> GET: https://schema.org/
2021-03-19 10:08:01.892:> Accept: */*
2021-03-19 10:08:01.892:< 200 https://schema.org/
2021-03-19 10:08:01.892:< Access-Control-Allow-Credentials: true
2021-03-19 10:08:01.892:< Access-Control-Allow-Headers: Accept
2021-03-19 10:08:01.892:< Access-Control-Allow-Methods: GET
2021-03-19 10:08:01.892:< Access-Control-Allow-Origin: *
2021-03-19 10:08:01.893:< Access-Control-Expose-Headers: Link
2021-03-19 10:08:01.893:< Age: 229
2021-03-19 10:08:01.893:< Alt-Svc: h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
2021-03-19 10:08:01.893:< Cache-Control: public, max-age=600
2021-03-19 10:08:01.893:< Content-Encoding: gzip
2021-03-19 10:08:01.893:< Content-Length: 2206
2021-03-19 10:08:01.893:< Content-Type: text/html
2021-03-19 10:08:01.893:< Date: Fri, 19 Mar 2021 14:04:12 GMT
2021-03-19 10:08:01.893:< ETag: "z2afww"
2021-03-19 10:08:01.893:< Expires: Fri, 19 Mar 2021 14:14:12 GMT
2021-03-19 10:08:01.893:< Link: </docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"
2021-03-19 10:08:01.893:< Server: Google Frontend
2021-03-19 10:08:01.893:< X-Cloud-Trace-Context: 72fe99328f0f0e7869ce616b1efc6e64;o=3
2021-03-19 10:08:01.893:< 0.0619 sec
2021-03-19 10:08:01.894:L Follow Link: https://schema.org/docs/jsonldcontext.jsonld
2021-03-19 10:08:01.914:> GET: https://schema.org/docs/jsonldcontext.jsonld
2021-03-19 10:08:01.914:> Accept: */*
2021-03-19 10:08:01.914:< 200 https://schema.org/docs/jsonldcontext.jsonld
2021-03-19 10:08:01.915:< Access-Control-Allow-Credentials: true
2021-03-19 10:08:01.915:< Access-Control-Allow-Headers: Accept
2021-03-19 10:08:01.915:< Access-Control-Allow-Methods: GET
2021-03-19 10:08:01.915:< Access-Control-Allow-Origin: *
2021-03-19 10:08:01.915:< Age: 450
2021-03-19 10:08:01.915:< Alt-Svc: h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
2021-03-19 10:08:01.915:< Cache-Control: public, max-age=600
2021-03-19 10:08:01.915:< Content-Length: 163023
2021-03-19 10:08:01.915:< Content-Type: application/ld+json
2021-03-19 10:08:01.915:< Date: Fri, 19 Mar 2021 14:00:31 GMT
2021-03-19 10:08:01.915:< ETag: "z2afww"
2021-03-19 10:08:01.915:< Expires: Fri, 19 Mar 2021 14:10:31 GMT
2021-03-19 10:08:01.915:< Server: Google Frontend
2021-03-19 10:08:01.915:< X-Cloud-Trace-Context: eceac0df35d0f09e46ebe05068460ef7;o=1
2021-03-19 10:08:01.915:< 0.0154 sec
2021-03-19 10:08:01.915:L Match linked type application/ld+json
2021-03-19 10:08:01.986:SUMMARY: Start URL: http://schema.org/
2021-03-19 10:08:01.986:SUMMARY: Final URL: https://schema.org/docs/jsonldcontext.jsonld
2021-03-19 10:08:01.986:SUMMARY: Start: 2021-03-19T14:08:01+0000
2021-03-19 10:08:01.986:SUMMARY: Num requests: 3
2021-03-19 10:08:01.986:SUMMARY: Elapsed: 0.140 seconds
{
  "@context": {
        "type": "@type",
        "id": "@id",
        "HTML": { "@id": "rdf:HTML" },

        "@vocab": "http://schema.org/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "schema": "http://schema.org/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
        "dctype": "http://purl.org/dc/dcmitype/",
        "void": "http://rdfs.org/ns/void#",
        "dcat": "http://www.w3.org/ns/dcat#",
        "3DModel": {"@id": "schema:3DModel"},
...
```