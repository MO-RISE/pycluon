# pycluon

A python wrapper around [libcluon](https://github.com/chrberger/libcluon). `pycluon` aims to follow the API of libcluon as closely as possible to avoid surprises.

So far, `pycluon` wraps the following concepts from libcluon:
* Envelope
* OD4Session
* UDPSender
* UDPReceiver
* TCPConnection
* TCPServer

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

| `pycluon` version | `libcluon` version |
|------------------:|-------------------:|
|             0.1.0 |            0.0.140 |

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

See the [tests](tests/test_libcluon_wrappers.py#L87-L143) for usage of `UDPSender`, `UDPReceiver`, `TCPConnection` and `TCPServer`.