"""Serve a directory on localhost, using the first free port starting from the given one."""

import argparse
import functools
import http.server
import sys
from pathlib import Path

MAX_ATTEMPTS = 50


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.directory))
    for port in range(args.port, args.port + MAX_ATTEMPTS):
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            continue
    else:
        sys.exit(f"no free port in {args.port}-{args.port + MAX_ATTEMPTS - 1}")

    print(f"Serving {args.directory}/ at http://localhost:{port} (Ctrl+C to stop)", flush=True)
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
