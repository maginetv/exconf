# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import sys
import os
import logbook
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exconf import utils
try:
        from StringIO import StringIO
except ImportError:
        from io import StringIO


class UtilsTest(unittest.TestCase):
    def test__available_log_levels(self):
        self.assertEquals(utils.figure_out_log_level("notset"), 0)
        self.assertEquals(utils.figure_out_log_level("trace"), 9)
        self.assertEquals(utils.figure_out_log_level("debug"), 10)
        self.assertEquals(utils.figure_out_log_level("info"), 11)
        self.assertEquals(utils.figure_out_log_level("warning"), 13)
        self.assertEquals(utils.figure_out_log_level("error"), 14)
        self.assertEquals(utils.figure_out_log_level("critical"), 15)

    def test_verbosity(self):
        self.assertEquals(utils.verbosity_level_to_log_level(0), "warning")
        self.assertEquals(utils.verbosity_level_to_log_level(1), "info")
        for x in range(2, 10):
            self.assertEquals(utils.verbosity_level_to_log_level(x), "debug")

    def test_get_logger(self):
        self.assertTrue(type(utils.get_logger()) is logbook.base.Logger)

    def test_read_yaml(self):
        self.assertEquals(utils.read_yaml("./tests/resources/file.yaml"), {'foo': {'bar': ['meh', 'zhe']}})

    def test_read_yaml_file_not_present(self):
        out = StringIO()
        self.assertEquals(utils.read_yaml("./tests/resources/null.yaml", out=out), None)
        self.assertEquals(out.getvalue().strip(), "Oops! That was no file in ./tests/resources/null.yaml.")

    def test_read_yaml_file_not_valid(self):
        out = StringIO()
        self.assertEquals(utils.read_yaml("./tests/resources/invalid.yaml", out=out), None)
        self.assertEquals(out.getvalue().strip(), "Oops! File ./tests/resources/invalid.yaml is not a valid yaml.")
