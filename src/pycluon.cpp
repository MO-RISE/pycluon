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

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <string>
#include <vector>

#include "cluon/Envelope.hpp"
#include "cluon/OD4Session.hpp"

namespace py = pybind11;
using namespace pybind11::literals;

PYBIND11_MODULE(_pycluon, m) {
  m.doc() = R"docs(
    A python wrapper around libcluon
  )docs";

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
          "sent",
          [](cluon::data::Envelope& envelope) {
            double seconds = static_cast<double>(envelope.sent().seconds());
            double microseconds =
                static_cast<double>(envelope.sent().microseconds());
            return seconds + microseconds / 10e6;
          },
          [](cluon::data::Envelope& envelope, double timestamp) {
            size_t seconds = static_cast<size_t>(timestamp);
            size_t microseconds = static_cast<size_t>(
                (timestamp - static_cast<double>(seconds)) * 10e6);

            cluon::data::TimeStamp tmp;
            tmp.seconds(seconds);
            tmp.microseconds(microseconds);
            envelope.sent(std::move(tmp));
          })
      .def_property(
          "received",
          [](cluon::data::Envelope& envelope) {
            double seconds = static_cast<double>(envelope.received().seconds());
            double microseconds =
                static_cast<double>(envelope.received().microseconds());
            return seconds + microseconds / 10e6;
          },
          [](cluon::data::Envelope& envelope, double timestamp) {
            size_t seconds = static_cast<size_t>(timestamp);
            size_t microseconds = static_cast<size_t>(
                (timestamp - static_cast<double>(seconds)) * 10e6);

            cluon::data::TimeStamp tmp;
            tmp.seconds(seconds);
            tmp.microseconds(microseconds);
            envelope.received(std::move(tmp));
          })
      .def_property(
          "sampled",
          [](cluon::data::Envelope& envelope) {
            double seconds =
                static_cast<double>(envelope.sampleTimeStamp().seconds());
            double microseconds =
                static_cast<double>(envelope.sampleTimeStamp().microseconds());
            return seconds + microseconds / 10e6;
          },
          [](cluon::data::Envelope& envelope, double timestamp) {
            size_t seconds = static_cast<size_t>(timestamp);
            size_t microseconds = static_cast<size_t>(
                (timestamp - static_cast<double>(seconds)) * 10e6);

            cluon::data::TimeStamp tmp;
            tmp.seconds(seconds);
            tmp.microseconds(microseconds);
            envelope.sampleTimeStamp(std::move(tmp));
          })
      .def_property(
          "sender_stamp",
          [](cluon::data::Envelope& self) { return self.senderStamp(); },
          [](cluon::data::Envelope& self, u_int32_t sender_stamp) {
            self.senderStamp(sender_stamp);
          });

  py::class_<cluon::OD4Session>(m, "OD4Session")
      .def(py::init<u_int16_t,
                    std::function<void(cluon::data::Envelope && envelope)>>(),
           "CID"_a, "delegate"_a = nullptr)
      .def("send",
           [](cluon::OD4Session& self, cluon::data::Envelope& envelope) {
             self.send(std::move(envelope));
           })
      .def("add_data_trigger", &cluon::OD4Session::dataTrigger)
      .def("set_time_trigger", &cluon::OD4Session::timeTrigger)
      .def("is_running", &cluon::OD4Session::isRunning);
}