import nose
from nose.plugins.cover import Coverage
import os,sys
import time
import coverage

# Rewrite the coverage plugin to extend it

old_options = Coverage.options
old_configure = Coverage.configure

def new_options(self, parser, env=os.environ):
   global old_options
   old_options(self, parser, env)
   parser.add_option("--cover-output-file",
                     default=None,
                     help="File to write coverage report.")
   parser.add_option("--xcover-output-file",
                     default=None,
                     help="File to write xunit coverage report. (cobertura-style xml)")

def new_configure(self, options, config):
   global old_configure
   old_configure(self, options, config)
   self.coverOutputFile = options.cover_output_file
   self.xcoverOutputFile = options.xcover_output_file

def new_report(self, stream):
   start_time = time.time()
   #log.debug("Coverage report")
   cover_inst = self.coverInstance
   cover_inst.stop()
   modules = [ module
                for name, module in sys.modules.items()
                if self.wantModuleCoverage(name, module) ]
   #log.debug("Coverage report will cover modules: %s", modules)
   cover_inst.report(modules, file=stream)
   if self.coverOutputFile:
      out_file = file(self.coverOutputFile,"w")
      cover_inst.report(modules, file=out_file)
   if self.xcoverOutputFile:
      morfs = [m.__file__ for m in modules if hasattr(m, '__file__') ]
      cover_inst.xml_report(morfs, outfile=self.xcoverOutputFile)

   stream.write("Overall coverage report time: %.2f\n\n" % (time.time() - start_time))

print "Overriding coverage package"
Coverage.options   = new_options
Coverage.configure = new_configure
Coverage.report    = new_report
