# Test runner.
import os
import datetime
import traceback
import re
import xml.dom.minidom

import nose
from nose.plugins import Plugin
import nose.plugins.builtin

try:
   import xml.etree.ElementTree as ET
except:
   import elementtree.ElementTree as ET


def writePrettyXML(root, filename):
   """ Helper to convert an ET Element into pretty formatted XML. """
   #sLeadSpacesRe  = re.compile('>\s+')
   #sTrailSpacesRe = re.compile('\s+<')
   text = ET.tostring(root)
   #text = sLeadSpacesRe.sub('>', text)
   #text = sTrailSpacesRe.sub('<', text)
   dom = xml.dom.minidom.parseString(text)
   dom.normalize()
   pretty_text = dom.toprettyxml(indent = '   ', newl = '\n')
   
   output_file = file(filename, 'w')
   output_file.write(pretty_text)
   output_file.close()

class XmlOutputPlugin(Plugin):
   """ XML Output Plugin proves an XML report output for nose tests.

   Dependencies: nose, elementtree
   
   Supports selection of multiple output formats. Output formats are implemented
   using a strategy pattern that selects a builder to use for the given format.
   The builder is responsible for building the xml elements for the report.

   Options:
      --xml-report: Set to the name of the file where the report should be sent.  If this option
                    is not set, then the plugin does not run.
      --xml-accumulate: will open and insert additional test results into an already existing 
          xml file. The intention is to allow multiple independent runs of 
          nosetest to create a single report.
      --xml-format: The name of the format builder to use for the xml output.  This allows
          users to select from one of the installed builders to change the structure of the
          xml output.
	  
   Extending:
   
      User can add new output formatters by creating a class that implements the formatter
      interface and then adding that class to the format map.
      
      Ex:  XmlOutputPlugin.format_map["my_format"] = MyXmlBuilder

   """
   name  = 'xml-output'
   score = 2   # run late (like html example)
   format_map = {}   # Map from format name to class that implements it

   def __init__(self):
      super(XmlOutputPlugin, self).__init__()
      self.root = None
      self.formatBuilder = None
      self.reportFileName = None
      self.accumulate = False
      self.format_map["nose"] = NoseXmlBuilder

   def options(self, parser, env):
      #super(XmlOutputPlugin, self).options(parser, env)
      parser.add_option("--xml-report",
                        dest = "xml_report", default=None,
                        help = "write an xml report of the output to the given file")
      parser.add_option("--xml-accumulate", action="store_true", dest="xml_accumulate", default=False,
                       help="Accumulate reults into report file, or start new")
      parser.add_option("--xml-format", type="choice", choices=self.format_map.keys(), default="nose",
	 help="Choose the format to use for the xml data output. options: %s  def: nose"%
	       self.format_map.keys())
   
   def configure(self, options, conf):
      super(XmlOutputPlugin, self).configure(options, conf)
      self.reportFileName = options.xml_report
      self.accumulate     = options.xml_accumulate
      if self.reportFileName != None:
      	 self.enabled = True
      self.formatBuilder = self.format_map[options.xml_format]()

   def begin(self):
      # If file already exists and we are accumulating, then use it
      if self.accumulate and os.path.exists(self.reportFileName):
	 try:
	    tree = ET.parse(self.reportFileName)
	    self.root = tree.getroot()
	 except IOError:
	    pass
      if self.root is None:
	 self.root = self.formatBuilder.buildRoot()
     
   def finalize(self, result):
      writePrettyXML(self.root, self.reportFileName)      

   def addError(self, test, err):
      new_elt = self.formatBuilder.buildError(test,err)
      text = ET.tostring(new_elt)
      self.root.append(new_elt)

   def addFailure(self, test, err):
      new_elt = self.formatBuilder.buildFailure(test,err)
      text = ET.tostring(new_elt)
      self.root.append(new_elt)

   def addSuccess(self, test):
      new_elt = self.formatBuilder.buildSuccess(test)
      text = ET.tostring(new_elt)
      self.root.append(new_elt)


class NoseXmlBuilder(object):
   """ XML builder for the 'nose' format.

   <testset>
      <meta>
	 <datetime>2006-08-14 14:37:37.679480</datetime>
      </meta>
      
      <test status="skipped" id="package.module.class.function" />
      
      <test status="success" id="package.module.class.function">
	 <capture>1+1=2</capture>
      </test>

      <test status="failure" id="package.module.class.function">
	 <capture />
	 <type>AssertionFailure</type>
	 <traceback>
	    <frame file="/home/richard/testproject/foo.py" line="100" function="callTest">
		    test("fish")
	    </frame>
	    <frame file="/home/richard/testproject/foo.py" line="120" function="test">
		    Assert True == False
	    </frame>
	 </traceback>
      </test>

      <test status="error" id="package.module.class.function" type=exceptions.RuntimeError'>
	 <capture>Who knows what generates one of these?</capture>
      </test>
   </testset>

   Note: This builder is based on code from NoseXML.
   """
   
   def buildRoot(self):
      """ Create a new root """
      root        = ET.Element("testset")
      metaElement = ET.SubElement(root, "meta")
      ET.SubElement(metaElement, "datetime").text = str(datetime.datetime.now())
      return root

   def finalize(self, result):
      """ Write out report as serialized XML """
      self.tree.write(self.reportFile)

   def buildSuccess(self, test):
      """
      Test was successful      
      """
      e = ET.Element("test", 
	 {"status": "success",
	  "id"    : test.id()})
      return e
	
   def buildFailure(self, test, error):
      """
      Test failed      
      """
      e = ET.Element("test")
      e.set("status", "failure")
      e.set("id", test.id())
      ET.SubElement(e, "capture").capture = error[1]
      ET.SubElement(e, "type").text = ''.join(traceback.format_exception_only(error[0],""))
      tracebackElement = ET.SubElement(e, "traceback")
      for (fname, line, func, text)  in traceback.extract_tb(error[2]):
	 frameElement = ET.SubElement(tracebackElement, "frame")
	 frameElement.set("file", fname)
	 frameElement.set("line", str(line))
	 frameElement.set("function", str(func))
	 frameElement.text = text
      return e

   def buildError(self, test, error):
      """
      Test errored. Not sure what causes this
      """
      e = ET.Element("test",
	 {"status":"error",
	  "id"    : test.id(),
	  "type"  : str(error[0])})
      ET.SubElement(e, "capture").text = str(error[1])
      return e


class BittenXmlBuilder(object):
   """ XML builder for the 'bitten' format.
   
       This can be used as a report format for te bitten continuous integration tool
       
      <report category="test">      
         <test name="test_config_update_name" fixture="package.test.TestCase"
            status="success|error|failure" duration="0.05"
	    file="test/test_me.py">
	    <description>Longer description</description>
	    <stdout>Renaming build configuration</stdout>
	    <stderr>error: did bad stuff</stderr>
	    <traceback>Full traceback details</traceback>
         </test>
      </report>
   """
   
   def buildRoot(self):
      """ Create a new root """
      return ET.Element("report",
		       {"category":"test"})
   
   def _buildCommon(self, test):
      e = ET.Element("test")
      description = test.shortDescription() or ''
      if description.startswith('doctest of '):
	 name = 'doctest'
	 fixture = description[11:]
	 description = None
      elif description.startswith("Doctest: "):
	 name = 'doctest'
	 fixture = description
      else:
	 name = test.id().split('.')[-1]
         fixture = ".".join( test.id().split('.')[:-1] )
      
      # Determine file path (try to get relative path)
      file_name = os.path.abspath(test.address()[0])
      prefix = os.path.commonprefix([os.getcwd(), file_name])
      file_name = file_name[len(prefix)+1:]                    # Strip off the common prefix
      if file_name.endswith(".pyc"):
	 file_name = file_name[:-1]
      
      e.set("name", name)
      e.set("fixture", fixture)
      e.set("file", file_name)
      if description:
	 ET.SubElement(e, "description").text = description
      
      return e
      
      
   def buildSuccess(self, test):
      """
      Test was successful      
      """
      e = self._buildCommon(test)
      e.set('status', "success")
      if hasattr(test,"captured_output"):
	 ET.SubElement(e, 'stdout').text = test.captured_output
      return e
	
   def buildFailure(self, test, error):
      e = self._buildCommon(test)
      e.set("status", "failure")
      
      capture_output = error[1]
      tb_string = "".join(traceback.format_exception(*error))
      ET.SubElement(e, 'stdout').text = capture_output
      ET.SubElement(e, 'traceback').text = tb_string
      return e

   def buildError(self, test, error):
      e = self._buildCommon(test)
      e.set("status", "error")
      
      capture_output = str(error[1])
      tb_string = "".join(traceback.format_exception(*error))
      ET.SubElement(e, 'stdout').text = capture_output
      ET.SubElement(e, 'traceback').text = tb_string
      
      text = ET.tostring(e)
      
      return e

XmlOutputPlugin.format_map["bitten"] = BittenXmlBuilder

# XXX: Hack for now to add this to the builtin plugins
nose.plugins.builtin.plugins.append(XmlOutputPlugin)
