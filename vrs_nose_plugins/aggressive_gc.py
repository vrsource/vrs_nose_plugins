import gc

import nose
from nose.plugins.base import Plugin


class AggressiveCollection(Plugin):
   """
   This plug-in provides a means to enable garbage collection at various points during test suite
   execution. If enabled, the default behavior is to run C{gc.collect(2)} during the test suite
   finalization.
   """
   name = 'gc'
   score = 3000

   def __init__(self):
      Plugin.__init__(self)
      self._gen       = 2
      self._gcPerCtxt = False
      self._gcPerDir  = False
      self._gcPerTest = False

   def options(self, parser, env):
      """
      Sets additional command line options.
      """
      Plugin.options(self, parser, env)
      parser.add_option(
         '--gc-per-context', action = 'store_true', dest = 'gc_per_context',
         default = env.get('NOSE_GC_PER_CONTEXT', self._gcPerCtxt),
         help = ("Perform garbage collection after each context. "
                 "Default is %s [NOSE_GC_PER_CONTEXT]" % self._gcPerCtxt)
      )
      parser.add_option(
         '--gc-per-directory', action = 'store_true', dest = 'gc_per_directory',
         default = env.get('NOSE_GC_PER_DIRECTORY', self._gcPerDir),
         help = ("Perform garbage collection after each directory. "
                 "Default %is s [NOSE_GC_PER_DIRECTORY]" % self._gcPerDir)
      )
      parser.add_option(
         '--gc-per-test', action = 'store_true', dest = 'gc_per_test',
         default = env.get('NOSE_GC_PER_TEST', self._gcPerTest),
         help = ("Perform garbage collection after each test. This can be VERY slow! "
                 "Default is %s [NOSE_GC_PER_TEST]" % self._gcPerTest)
      )
      parser.add_option(
         '--gc-gen', action = 'store', dest = 'gc_gen',
         default = env.get('NOSE_GC_GEN', self._gen),
         help = "Garbage collection generation to run. Default is %d [NOSE_GC_GEN]" % self._gen
      )

   def configure(self, options, config):
      """
      Configures the gc plugin.
      """
      Plugin.configure(self, options, config)
      self.config = config
      if self.enabled:
         self._gen       = int(options.gc_gen)
         self._gcPerCtxt = options.gc_per_context
         self._gcPerDir  = options.gc_per_directory
         self._gcPerTest = options.gc_per_test

   def afterContext(self):
      """
      Called after a context (generally a module) has been lazy-loaded, imported, setup, had its
      tests loaded and executed, and torn down.
      """
      if self._gcPerCtxt:
         gc.collect(self._gen)

   def afterDirectory(self, path):
      """
      Called after all tests have been loaded from directory at path and run.
      """
      if self._gcPerDir:
         gc.collect(self._gen)

   def afterTest(self, test):
      """
      Called after the test has been run and the result recorded (after L{stopTest}).
      """
      if self._gcPerTest:
         gc.collect(self._gen)

   def finalize(self, result):
      """
      Called after all report output, including output from all plugins, has been sent to the
      stream.
      """
      gc.collect(2)


# XXX: Hack for now to add this to the builtin plugins
nose.plugins.builtin.plugins.append(AggressiveCollection)
