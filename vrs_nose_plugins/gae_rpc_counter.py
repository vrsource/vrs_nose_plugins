# Test runner.
import os
import time
import sys

import nose
from nose.plugins import Plugin
import nose.plugins.builtin


class GaeRpcCountsPlugin(Plugin):
   """
   Nose plugin to track Google App Engine RPC calls in tests.

   Collects the timing information computed by our test classes.

   Dependencies: nose
   """
   name  = 'rpc-count'
   score = 3         # run late (like html example)

   def __init__(self):
      super(GaeRpcCountsPlugin, self).__init__()
      self._detailed     = False
      self._rpcCounts    = []  # List of (test_name, count, rpcLog)

   def options(self, parser, env):
      super(GaeRpcCountsPlugin, self).options(parser, env)
      parser.add_option("--rpc-count-detailed", action="store_true",
                        dest = "rpc_count_detailed", default = False,
                        help = "Track extra details for rpc calls")
      parser.add_option("--rpc-count-sort", action="store_true",
                        dest = "rpc_count_sort", default = False,
                        help = "Sort rpc count from high to low")

   def configure(self, options, config):
      super(GaeRpcCountsPlugin, self).configure(options, config)
      if not self.enabled:
         return
      self._detailed = options.rpc_count_detailed
      self._sort     = options.rpc_count_sort


   def begin(self):
      pass

   def startTest(self, test):
      pass

   def stopTest(self, test):
      # Check if they are one of our CommonTestCase tests, and if so, collect the info
      # about the rpc counts.
      test_obj = test.test
      if hasattr(test_obj, '_rpcCount'):
         self._rpcCounts.append([str(test), test.test._rpcCount, test.test._rpcLog])


   def report(self, stream):
      """ Write out the results. """
      if self._sort:
         self._rpcCounts.sort(key = lambda x:x[1], reverse = True)

      stream.write("-------- RPC Report ---------\n")

      for (name, count, rpc_log) in self._rpcCounts:
         stream.write("[%4d] %s\n" % (count, name))
         if self._detailed:
            all_items = rpc_log.items()
            all_items.sort(key = lambda x:x[1], reverse = True)
            for (k, v) in all_items:
               stream.write("   (%3d) %s\n" % (v, k))


      #stream.write("\n\n   --- Slowest %s Tests ---\n" % self._numSlowestTests)
      #self._profResults.sort(key = lambda x:x[1], reverse = True)
      #for x in range(min(self._numSlowestTests, len(self._profResults))):
      #   (test_name, duration) = self._profResults[x]
      #   stream.write("[%2.4f] %s\n" % (duration, test_name))
      return None  # Allow others to report



# XXX: Hack for now to add this to the builtin plugins
nose.plugins.builtin.plugins.append(GaeRpcCountsPlugin)
