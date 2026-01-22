#!/usr/bin/env python3
import subprocess
import threading
import socket
import select
import sys
import time
import signal

HOST = "127.0.0.1"
PORT = 19021

JLINK_CMD = [
    "JLinkExe",
    "-device", "NRF52840_XXAA",
    "-if", "SWD",
    "-speed", "4000",
    "-autoconnect", "1",
]

IAC = 255  # Telnet "Interpret As Command" (0xFF)


class RTTSession:
    def __init__(self):
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._rx_thread = None
        self._jlink_thread = None
        self._sock = None
        self._proc = None
        self._seen_payload = False

    def start(self):
        with self._lock:
            self._stop_evt.clear()
            self._seen_payload = False

            self._proc = subprocess.Popen(
                JLINK_CMD,
                stdin=subprocess.PIPE,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
                bufsize=1,
            )

            time.sleep(1.0)

            self._sock = socket.create_connection((HOST, PORT))

            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()

            self._jlink_thread = threading.Thread(target=self._jlink_watchdog, daemon=True)
            self._jlink_thread.start()

    def stop(self):
        with self._lock:
            self._stop_evt.set()
            sock = self._sock
            rx = self._rx_thread
            proc = self._proc

        if sock is not None:
            sock.shutdown(socket.SHUT_RDWR)

        if rx is not None:
            rx.join()

        with self._lock:
            sock = self._sock
            self._sock = None
            self._rx_thread = None

        if sock is not None:
            sock.close()

        if proc is not None:
            proc.stdin.write("q\n")
            proc.stdin.flush()
            proc.terminate()
            proc.wait()

        with self._lock:
            self._proc = None
            self._jlink_thread = None

    def restart(self):
        self.stop()
        self.start()

    def jlink_reset(self):
        with self._lock:
            proc = self._proc
        if proc is not None and proc.stdin is not None:
            proc.stdin.write("r\n")
            proc.stdin.flush()

    def send(self, text: str):
        with self._lock:
            sock = self._sock
        if sock is not None:
            sock.sendall(text.encode("utf-8"))

    def _rx_loop(self):
        with self._lock:
            sock = self._sock

        while not self._stop_evt.is_set():
            rlist, _, _ = select.select([sock], [], [], 0.1)
            if not rlist or self._stop_evt.is_set():
                continue

            data = sock.recv(4096)
            if data == b"":
                self._stop_evt.set()
                break

            data = self._strip_telnet_and_normalize(data)

            if not self._seen_payload and data.strip() == b"":
                continue
            self._seen_payload = True

            sys.stdout.buffer.write(data)
            sys.stdout.flush()

    def _strip_telnet_and_normalize(self, data: bytes) -> bytes:
        out = bytearray()
        i = 0
        n = len(data)

        while i < n:
            b = data[i]
            if b != IAC:
                out.append(b)
                i += 1
                continue

            if i + 1 < n and data[i + 1] == IAC:
                out.append(IAC)
                i += 2
                continue

            if i + 2 < n:
                i += 3
            else:
                i = n

        data = bytes(out)
        data = data.replace(b"\x00", b"")
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return data

    def _jlink_watchdog(self):
        with self._lock:
            proc = self._proc
        while not self._stop_evt.is_set():
            if proc.poll() is not None:
                self._stop_evt.set()
                break
            time.sleep(0.1)


def main():
    sess = RTTSession()
    sess.start()

    def on_sigint(signum, frame):
        sess.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, on_sigint)

    while True:
        line = sys.stdin.readline()
        if line == "":
            sess.stop()
            break

        cmd = line.strip()

        if cmd.lower() == "Q":
            sess.stop()
            break

        if cmd == "R":
            sess.restart()
            continue

        if cmd == "J":
            sess.jlink_reset()
            continue

        sess.send(line)

if __name__ == "__main__":
    main()

