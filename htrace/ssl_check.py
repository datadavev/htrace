import logging
import socket
import ssl
import certifi

# hacky pile - seems there's an option probably coming in 3.10 for direct access to peer cert chain
# https://github.com/python/cpython/pull/25467

L = logging.getLogger("ssl_check")

def sslWrapSocket(sock, keyfile=None, certfile=None, cert_reqs=None,
                    ca_certs=None, server_hostname=None,
                    ssl_version=None):
    context = ssl.SSLContext(ssl_version)
    context.verify_mode = cert_reqs

    if ca_certs:
        try:
            context.load_verify_locations(ca_certs)
        # Py32 raises IOError
        # Py33 raises FileNotFoundError
        except Exception as e:  # Reraise as SSLError
            L.debug("load verify_locations failed: %s", ca_certs)
            raise ssl.SSLError(e)

    if certfile:
        # FIXME: This block needs a test.
        context.load_cert_chain(certfile, keyfile)

    if ssl.HAS_SNI:  # Platform-specific: OpenSSL with enabled SNI
        return (context, context.wrap_socket(sock, server_hostname=server_hostname))

    return (context, context.wrap_socket(sock))


def sslCheck(host_name, port=443):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    s.settimeout(10)
    s.connect((host_name, port))

    (context, ssl_socket) = sslWrapSocket(s,
                                           ssl_version=ssl.PROTOCOL_TLS,
                                           cert_reqs=ssl.CERT_REQUIRED,
                                           ca_certs=certifi.where(),
                                           server_hostname=host_name)
    #conn.setblocking(1)
    #conn.do_handshake()
    #conn.set_tlsext_host_name(hostname.encode())
    res = ssl_socket.getpeercert()
    return res

def test():
    import socket

    from ssl import wrap_socket, CERT_NONE, PROTOCOL_SSLv23
    from ssl import SSLContext  # Modern SSL?
    from ssl import HAS_SNI  # Has SNI?

    from pprint import pprint

    def ssl_wrap_socket(sock, keyfile=None, certfile=None, cert_reqs=None,
                        ca_certs=None, server_hostname=None,
                        ssl_version=None):
        context = SSLContext(ssl_version)
        context.verify_mode = cert_reqs

        if ca_certs:
            try:
                context.load_verify_locations(ca_certs)
            # Py32 raises IOError
            # Py33 raises FileNotFoundError
            except Exception as e:  # Reraise as SSLError
                raise ssl.SSLError(e)

        if certfile:
            # FIXME: This block needs a test.
            context.load_cert_chain(certfile, keyfile)

        if HAS_SNI:  # Platform-specific: OpenSSL with enabled SNI
            return (context, context.wrap_socket(sock, server_hostname=server_hostname))

        return (context, context.wrap_socket(sock))

    hostname = 'www.google.com'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 443))

    (context, ssl_socket) = ssl_wrap_socket(s,
                                            ssl_version=2,
                                            cert_reqs=2,
                                            ca_certs=certifi.where(),
                                            server_hostname=hostname)

    pprint(dir(ssl_socket))
    pprint(ssl_socket.getpeercert())

    s.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import pprint
    #pprint.pprint(sslCheck("api.geosamples.org"))
    #pprint.pprint(sslCheck("google.com"))
    test()
