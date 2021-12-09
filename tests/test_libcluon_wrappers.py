import time
import gc
import sys
import threading
from datetime import datetime

import pytest

from pycluon._pycluon import (
    Envelope,
    OD4Session,
    UDPSender,
    UDPReceiver,
    TCPConnection,
    TCPServer,
    SharedMemory,
)


def test_envelope_setters_getters():
    e = Envelope()

    assert e.data_type == 0
    e.data_type = 53
    assert e.data_type == 53

    assert e.serialized_data == b""
    e.serialized_data = b"muppet"
    assert e.serialized_data == b"muppet"

    assert isinstance(e.sent_at, datetime)
    assert e.sent_at.timestamp() == 0.0
    e.sent_at = datetime.fromtimestamp(347238.438274)
    assert e.sent_at.timestamp() == 347238.438274

    assert isinstance(e.received_at, datetime)
    assert e.received_at.timestamp() == 0.0
    e.received_at = datetime.fromtimestamp(347238.438274)
    assert e.received_at.timestamp() == 347238.438274

    assert isinstance(e.sampled_at, datetime)
    assert e.sampled_at.timestamp() == 0.0
    e.sampled_at = datetime.fromtimestamp(347238.438274)
    assert e.sampled_at.timestamp() == 347238.438274

    assert e.sender_stamp == 0
    e.sender_stamp = 53
    assert e.sender_stamp == 53


def test_OD4Session_time_trigger():
    od = OD4Session(111)

    _called = 0

    def callback():
        nonlocal _called
        _called += 1
        if _called >= 3:
            return False

        return True

    od.set_time_trigger(10, callback)

    assert _called == 3


def test_OD4Session_send_data_trigger():
    od1 = OD4Session(111)
    od2 = OD4Session(111)

    sender = 13
    message_id = 31

    _called = False

    def callback(envelope):
        nonlocal _called, sender, message_id
        if envelope.sender_stamp == sender and envelope.data_type == message_id:
            _called = True

    od1.add_data_trigger(message_id, callback)

    e = Envelope()
    e.data_type = message_id
    e.sender_stamp = sender

    od2.send(e)

    time.sleep(0.01)

    assert _called


def test_UDP_ping():
    received = {}

    def receive_callback(data, sender, timestamp):
        nonlocal received
        received["data"] = data
        received["sender"] = sender
        received["timestamp"] = timestamp

    r = UDPReceiver("127.0.0.1", 50032, receive_callback)

    size, error = UDPSender("127.0.0.1", 50032).send("test")

    assert size == 4
    assert error == 0

    time.sleep(0.1)

    assert received["data"] == "test"
    assert isinstance(received["timestamp"], datetime)


def test_TCP_ping():
    CALLED_ON_CONNECTION = False

    def on_connection(connectee, connection):
        nonlocal CALLED_ON_CONNECTION
        CALLED_ON_CONNECTION = True
        assert isinstance(connectee, str)
        assert isinstance(connection, TCPConnection)

        connection.send("test")

    server = TCPServer(50033, on_connection)

    CALLED_ON_CONNECTION_LOST = False

    def on_connection_lost():
        nonlocal CALLED_ON_CONNECTION_LOST
        CALLED_ON_CONNECTION_LOST = True

    CALLED_ON_MESSAGE = False

    def on_message(data, timestamp):
        nonlocal CALLED_ON_MESSAGE
        CALLED_ON_MESSAGE = True
        assert data == "test"

    user = TCPConnection("127.0.0.1", 50033, on_message, on_connection_lost)

    time.sleep(0.1)
    assert CALLED_ON_CONNECTION
    assert CALLED_ON_MESSAGE

    del server
    gc.collect()

    assert CALLED_ON_CONNECTION_LOST


# @pytest.mark.skipif(
#     sys.platform == "win32" or sys.platform == "darwin",
#     reason="See issue https://github.com/MO-RISE/pycluon/issues/11",
# )
def test_shared_memory():
    sm = SharedMemory("trial.data", 10)
    sm2 = SharedMemory("trial.data")

    print(sm.name())

    assert sm.valid()
    assert sm2.valid()

    assert len(sm.data) == 10
    assert len(sm2.data) == 10

    assert sm.data == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    assert sm2.data == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    assert not sm.is_locked()
    assert not sm2.is_locked()

    sm.lock()
    assert sm.is_locked()
    assert not sm2.is_locked()
    sm.unlock()

    sm2.lock()
    assert sm2.is_locked()
    assert not sm.is_locked()
    sm2.unlock()

    with pytest.raises(BufferError):
        sm.timestamp = datetime.now()

    sm.lock()
    dt = sm.timestamp = datetime.now()

    with pytest.raises(TypeError):
        sm.data = "abcdefghij"

    sm.data = b"abcdefghij"  # len == 10
    sm.unlock()

    sm2.lock()
    assert sm2.data == b"abcdefghij"
    assert sm2.timestamp == dt
    sm2.unlock()

    t = threading.Thread(target=sm2.wait, daemon=True)
    t.start()

    time.sleep(0.1)
    assert t.is_alive()

    sm.notify_all()

    time.sleep(0.1)
    assert not t.is_alive()
