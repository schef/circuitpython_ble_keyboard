#!/usr/bin/env python3
import asyncio
import sys
import time

HOST = "127.0.0.1"
PORT = 19021
JLINK_TAG = "JLNK"
SEGER_TAG = "SEGR"
ENABLE_COLOR = True
COLOR_JLINK = "\x1b[34m"
COLOR_SEGER = "\x1b[32m"
COLOR_RESET = "\x1b[0m"

JLINK_CMD = [
    "JLinkExe",
    "-device",
    "NRF52840_XXAA",
    "-if",
    "SWD",
    "-speed",
    "4000",
    "-autoconnect",
    "1",
]

IAC = 255  # Telnet "Interpret As Command" (0xFF)


def line_prefix(tag: str, color: str) -> bytes:
    now = time.time()
    timestamp = time.strftime("%H:%M:%S", time.localtime(now))
    millis = int((now - int(now)) * 1000)
    if ENABLE_COLOR and color:
        prefix = f"{color}[{tag}]{COLOR_RESET}[{timestamp}.{millis:03d}] "
    else:
        prefix = f"[{tag}][{timestamp}.{millis:03d}] "
    return prefix.encode("utf-8")


def strip_telnet(data: bytes) -> bytes:
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


async def connect_rtt_socket():
    deadline = time.time() + 5.0
    last_err = None
    while time.time() < deadline:
        try:
            return await asyncio.wait_for(
                asyncio.open_connection(HOST, PORT), timeout=1.0
            )
        except (OSError, asyncio.TimeoutError) as exc:
            last_err = exc
            await asyncio.sleep(0.2)
    raise RuntimeError(f"RTT socket connect failed: {last_err}")


async def rtt_reader(
    reader: asyncio.StreamReader,
    stop_evt: asyncio.Event,
    restart_evt: asyncio.Event,
):
    line_buffer = bytearray()
    while not stop_evt.is_set():
        data = await reader.read(4096)
        if data == b"":
            restart_evt.set()
            stop_evt.set()
            break
        data = strip_telnet(data)
        line_buffer.extend(data)
        while b"\n" in line_buffer:
            line, _, remainder = line_buffer.partition(b"\n")
            line_buffer = bytearray(remainder)
            prefix = line_prefix(SEGER_TAG, COLOR_SEGER)
            sys.stdout.buffer.write(prefix + line + b"\n")
            sys.stdout.flush()


async def stream_reader(stream, tag, color, stop_evt: asyncio.Event):
    if stream is None:
        return
    while not stop_evt.is_set():
        line = await stream.readline()
        if not line:
            break
        prefix = line_prefix(tag, color).decode("utf-8")
        text = line.decode("utf-8", errors="replace").rstrip("\n")
        sys.stdout.write(f"{prefix}{text}\n")
        sys.stdout.flush()


async def stdin_reader(stop_evt: asyncio.Event):
    while not stop_evt.is_set():
        line = await asyncio.to_thread(sys.stdin.readline)
        if line == "":
            stop_evt.set()
            return None
        return line


async def run_session():
    restart = False
    proc = await asyncio.create_subprocess_exec(
        *JLINK_CMD,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await asyncio.sleep(1.0)
    reader, writer = await connect_rtt_socket()
    stop_evt = asyncio.Event()
    restart_evt = asyncio.Event()

    tasks = [
        asyncio.create_task(rtt_reader(reader, stop_evt, restart_evt)),
        asyncio.create_task(
            stream_reader(proc.stdout, JLINK_TAG, COLOR_JLINK, stop_evt)
        ),
        asyncio.create_task(
            stream_reader(proc.stderr, JLINK_TAG, COLOR_JLINK, stop_evt)
        ),
    ]

    try:
        while not stop_evt.is_set():
            line = await stdin_reader(stop_evt)
            if line is None:
                break
            cmd = line.strip()
            if cmd == "Q":
                stop_evt.set()
                break
            if cmd == "R":
                restart = True
                stop_evt.set()
                break
            if cmd == "J":
                if proc.stdin is not None:
                    proc.stdin.write(b"r\n")
                    await proc.stdin.drain()
                continue
            if writer is not None:
                writer.write(line.encode("utf-8"))
                await writer.drain()
    finally:
        stop_evt.set()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except AttributeError:
                pass
        if proc.stdin is not None:
            proc.stdin.write(b"q\n")
            await proc.stdin.drain()
            proc.stdin.close()
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            proc.kill()
            await asyncio.wait_for(proc.wait(), timeout=2.0)
    return restart or restart_evt.is_set()


async def main_async():
    while True:
        restart = await run_session()
        if not restart:
            break
        await asyncio.sleep(0.2)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
