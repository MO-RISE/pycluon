# pycluon

A python wrapper around [libcluon](https://github.com/chrberger/libcluon). `pycluon` aims to follow the API of libcluon as closely as possible to avoid surprises.

So far, `pycluon` wraps the following concepts from libcluon:
* Envelope
* OD4Session
* UDPSender
* UDPReceiver
* TCPConnection
* TCPServer
* SharedMemory

It also bundles the following command-line applications:
* protoc
* cluon-msc
* cluon-OD4toStdout
* cluon-OD4toJSON
* cluon-LCMtoJSON
* cluon-filter
* cluon-livefeed
* cluon-rec2csv
* cluon-replay

## Versioning

| `pycluon` version | `libcluon` version | `python` versions            |
|------------------:|-------------------:|-----------------------------:|
|             0.1.0 |            0.0.140 | 3.7, 3.8, 3.9, 3.10          |
|             0.1.1 |            0.0.140 | 3.7, 3.8, 3.9, 3.10          |
|             0.1.2 |            0.0.140 | 3.7, 3.8, 3.9, 3.10          |
|             0.1.3 |            0.0.140 | 3.7, 3.8, 3.9, 3.10          |
|             0.2.0 |            0.0.140 | 3.7, 3.8, 3.9, 3.10          |
|             0.2.1 |            0.0.140 | 3.7, 3.8, 3.9, 3.10, 3.11    |
|             0.2.2 |            0.0.145 | 3.7, 3.8, 3.9, 3.10, 3.11    |

## Installation

`pycluon` is available on PyPI:

```
pip install pycluon
```

## Examples

**Import an odvd specification into a python module**
```python
from pycluon.importer import import_odvd

my_module = import_odvd("/path/to/my/odvd/specification.odvd")
```

**Send an envelope**
```python
import time
from pycluon import OD4Session, Envelope

session = OD4Session(111)

message = my_module.MyMessage()

envelope = Envelope()
envelope.sent = envelope.sampled = time.time()
envelope.serialized_data = message.SerializeToString()
envelope.data_type = 13
envelope.sender_stamp = 13

session.send(envelope)
```

**Receive an envelope**
```python
import time
from pycluon import OD4Session

session = OD4Session(111)

def callback(envelope):
    message = my_module.MyMessage()
    message.ParseFromString(envelope.serialized_data)
    print(f"Received at {envelope.received} seconds since epoch")

session.add_data_trigger(13, callback)

while session.is_running():
    time.sleep(0.01)
```

**Write to a shared memory area**
```python
from datetime import datetime
from pycluon import SharedMemory

sm = SharedMemory("frame.argb", 640*480)

sm.lock()
sm.timestamp = datetime.now()
sm.data = b"<bytes>"
sm.unlock()
sm.notify_all()
```

**Read from an existing shared memory area**
```python
from pycluon import SharedMemory

sm = SharedMemory("frame.argb")

sm.wait() # Wait for notification from writing process
sm.lock()
print(sm.timestamp)
print(sm.data)
sm.unlock()
```

See the [tests](tests/test_libcluon_wrappers.py#L87-L143) for usage of `UDPSender`, `UDPReceiver`, `TCPConnection` and `TCPServer`.
