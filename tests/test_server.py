import sys

import pytest

from pkl.server import PKLServer
from pkl.utils import PklError


def test_server():
    server = PKLServer()
    server.terminate()


@pytest.mark.timeout(10)
def test_server_raises_on_closed_stream():
    # Simulates a pkl server that crashes/exits before responding (JAJ-824):
    # PKLServer._read must detect the closed stdout pipe and raise, not spin
    # forever treating EOF (b"") the same as "no data yet" (None).
    server = PKLServer(cmd=[sys.executable, "-c", "import sys; sys.exit(1)"])
    try:
        with pytest.raises(PklError, match="closed its output stream"):
            server.receive()
    finally:
        server.terminate()
