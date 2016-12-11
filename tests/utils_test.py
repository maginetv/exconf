import unittest
import sys
sys.path.insert(0, '../exconf')
import utils


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

if __name__ == "__main__":
    unittest.main()
