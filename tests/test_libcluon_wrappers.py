import time
import gc

from pycluon._pycluon import (
    Envelope,
    OD4Session,
    UDPSender,
    UDPReceiver,
    TCPConnection,
    TCPServer,
)


def test_envelope_setters_getters():
    e = Envelope()

    assert e.data_type == 0
    e.data_type = 53
    assert e.data_type == 53

    assert e.serialized_data == b""
    e.serialized_data = b"muppet"
    assert e.serialized_data == b"muppet"

    assert e.sent == 0.0
    e.sent = 347238.438274
    assert e.sent == 347238.438274

    assert e.received == 0.0
    e.received = 347238.438274
    assert e.received == 347238.438274

    assert e.sampled == 0.0
    e.sampled = 347238.438274
    assert e.sampled == 347238.438274

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
