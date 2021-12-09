// Copyright 2021 RISE Research Institute of Sweden - Maritime Operations

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <pybind11/chrono.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <chrono>
#include <filesystem>
#include <string>
#include <thread>
#include <vector>

#include "cluon/Envelope.hpp"
#include "cluon/OD4Session.hpp"
#include "cluon/SharedMemory.hpp"
#include "cluon/TCPConnection.hpp"
#include "cluon/TCPServer.hpp"
#include "cluon/Time.hpp"
#include "cluon/UDPReceiver.hpp"
#include "cluon/UDPSender.hpp"
#include "cluon/cluonDataStructures.hpp"

namespace py = pybind11;
using namespace pybind11::literals;

std::chrono::system_clock::time_point to_timepoint(
    const cluon::data::TimeStamp& ts) {
  return std::chrono::system_clock::time_point(
      std::chrono::microseconds(cluon::time::toMicroseconds(ts)));
}

cluon::data::TimeStamp from_timepoint(
    const std::chrono::system_clock::time_point& tp) {
  return cluon::time::convert(tp);
}

PYBIND11_MODULE(_pycluon, m) {
  m.doc() = R"docs(
    A python wrapper around libcluon
  )docs";

  // Envelope
  py::class_<cluon::data::Envelope>(m, "Envelope")
      .def(py::init<>())
      .def_property(
          "data_type",
          [](cluon::data::Envelope& self) { return self.dataType(); },
          [](cluon::data::Envelope& self, size_t data_type) {
            self.dataType(data_type);
          })
      .def_property(
          "serialized_data",
          [](cluon::data::Envelope& self) {
            return py::bytes(self.serializedData());
          },
          [](cluon::data::Envelope& self, py::bytes serialized_data) {
            self.serializedData(serialized_data);
          })
      .def_property(
          "sent_at",
          [](cluon::data::Envelope& envelope) {
            return to_timepoint(envelope.sent());
          },
          [](cluon::data::Envelope& envelope,
             const std::chrono::system_clock::time_point& tp) {
            envelope.sent(from_timepoint(tp));
          })
      .def_property(
          "received_at",
          [](cluon::data::Envelope& envelope) {
            return to_timepoint(envelope.received());
          },
          [](cluon::data::Envelope& envelope,
             const std::chrono::system_clock::time_point& tp) {
            envelope.received(from_timepoint(tp));
          })
      .def_property(
          "sampled_at",
          [](cluon::data::Envelope& envelope) {
            return to_timepoint(envelope.sampleTimeStamp());
          },
          [](cluon::data::Envelope& envelope,
             const std::chrono::system_clock::time_point& tp) {
            envelope.sampleTimeStamp(from_timepoint(tp));
          })
      .def_property(
          "sender_stamp",
          [](cluon::data::Envelope& self) { return self.senderStamp(); },
          [](cluon::data::Envelope& self, uint32_t sender_stamp) {
            self.senderStamp(sender_stamp);
          });

  // OD4Session
  py::class_<cluon::OD4Session>(m, "OD4Session")
      .def(py::init<uint16_t,
                    std::function<void(cluon::data::Envelope && envelope)>>(),
           "CID"_a, "delegate"_a = nullptr)
      .def("send",
           [](cluon::OD4Session& self, cluon::data::Envelope& envelope) {
             self.send(std::move(envelope));
           })
      .def("add_data_trigger", &cluon::OD4Session::dataTrigger)
      .def("set_time_trigger", &cluon::OD4Session::timeTrigger)
      .def("is_running", &cluon::OD4Session::isRunning);

  // UDPReceiver
  py::class_<cluon::UDPReceiver>(m, "UDPReceiver")
      .def(py::init<
               const std::string&, uint16_t,
               std::function<void(std::string&&, std::string&&,
                                  std::chrono::system_clock::time_point &&)>,
               uint16_t>(),
           "receive_from_address"_a, "receive_from_port"_a, "delegate"_a,
           "local_send_from_port"_a = 0)
      .def("is_running", &cluon::UDPReceiver::isRunning);

  // UDPSender
  py::class_<cluon::UDPSender>(m, "UDPSender")
      .def(py::init<const std::string&, uint16_t>(), "send_to_address"_a,
           "send_to_port"_a)
      .def("send", &cluon::UDPSender::send)
      .def("get_send_from_port", &cluon::UDPSender::getSendFromPort);

  // TCPConnection
  py::class_<cluon::TCPConnection, std::shared_ptr<cluon::TCPConnection>>(
      m, "TCPConnection")
      .def(py::init<
               const std::string&, uint16_t,
               std::function<void(std::string&&,
                                  std::chrono::system_clock::time_point &&)>,
               std::function<void()>>(),
           "address"_a, "port"_a, "on_data_delegate"_a = nullptr,
           "on_connection_lost_delegate"_a = nullptr)
      .def("send", &cluon::TCPConnection::send)
      .def("is_running", &cluon::TCPConnection::isRunning);

  // TCPServer
  py::class_<cluon::TCPServer>(m, "TCPServer")
      .def(py::init<uint16_t, std::function<void(
                                  std::string&&,
                                  std::shared_ptr<cluon::TCPConnection>)>>(),
           "port"_a, "new_connection_delegate"_a)
      .def("is_running", &cluon::TCPServer::isRunning);

  // SharedMemory
  py::class_<cluon::SharedMemory>(m, "SharedMemory")
      .def(py::init<const std::string&, uint32_t>(), "name"_a, "size"_a = 0)
      .def("is_locked", &cluon::SharedMemory::isLocked)
      .def("lock", &cluon::SharedMemory::lock)
      .def("unlock", &cluon::SharedMemory::unlock)
      .def("wait", &cluon::SharedMemory::wait,
           py::call_guard<py::gil_scoped_release>())
      .def("notify_all", &cluon::SharedMemory::notifyAll)
      .def("valid", &cluon::SharedMemory::valid)
      .def("name", &cluon::SharedMemory::name)
      .def_property(
          "timestamp",
          [](cluon::SharedMemory& self) {
            auto [flag, ts] = self.getTimeStamp();
            if (!flag) {
              throw pybind11::buffer_error(
                  "The shared memory area is not locked!");
            }
            return to_timepoint(ts);
          },
          [](cluon::SharedMemory& self,
             const std::chrono::system_clock::time_point& tp) {
            if (!self.setTimeStamp(from_timepoint(tp))) {
              throw pybind11::buffer_error(
                  "The shared memory area is not locked!");
            }
          })

      .def_property(
          "data",
          [](cluon::SharedMemory& self) {
            return py::bytes(std::string(self.data(), self.size()));
          },
          [](cluon::SharedMemory& self, py::bytes data) {
            strcpy(self.data(), std::string(data).c_str());
          });
}