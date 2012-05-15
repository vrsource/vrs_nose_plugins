# Test runner.
import os
import time

import nose
from nose.plugins import Plugin
import nose.plugins.builtin


class TestTimerPlugin(Plugin):
   """
   Nose plugin to time tests.

   Collects the timing information on all tests and prints a report.

   Dependencies: nose
   """
   name  = 'time-tests'
   score = 2         # run late (like html example)

   def __init__(self):
      super(TestTimerPlugin, self).__init__()
      self._profResults = [] # List of (test name, time)
      self._testStartTime = None  # Absolute start time

   def options(self, parser, env):
      super(TestTimerPlugin, self).options(parser, env)
      parser.add_option("--time-tests-slowest-num", type="int",
                        dest = "time_tests_slowest_num", default = 10,
                        help = "Number of slowest tests to report")

   def configure(self, options, conf):
      super(TestTimerPlugin, self).configure(options, conf)
      self._numSlowestTests = options.time_tests_slowest_num

   def begin(self):
      self._testStartTime = time.time()

   def startTest(self, test):
      test._timer_startTime = time.time()

   def stopTest(self, test):
      duration = time.time() - test._timer_startTime
      self._profResults.append([str(test), duration])


   def report(self, stream):
      """ Write out the results. """
      stream.write("-------- Timing Report ---------\n")
      stream.write("Overall time: %.2f\n\n" % (time.time() - self._testStartTime))
#      for (test_name, duration) in self._profResults:
#         stream.write("[%2.4f] %s\n" % (duration, test_name))

      stream.write("\n\n   --- Slowest %s Tests ---\n" % self._numSlowestTests)
      self._profResults.sort(key = lambda x:x[1], reverse = True)
      for x in range(min(self._numSlowestTests, len(self._profResults))):
         (test_name, duration) = self._profResults[x]
         stream.write("[%2.4f] %s\n" % (duration, test_name))


      return None  # Allow others to report


# XXX: Hack for now to add this to the builtin plugins
nose.plugins.builtin.plugins.append(TestTimerPlugin)
