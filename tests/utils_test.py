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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from exconf import utils


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
