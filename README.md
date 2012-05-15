Background
==========

This package includes a variety of plugins that we have found useful on multiple projects.  Please take a look at the source for details.

Features
========
Items of note:

  * AgressiveCollection: Adds options for enabling garbage collection.
  * Extended Coverage: Adds support for writting coverage output to a file
  * GaeRpcCountsPlugin: Adds support for counting all rpc calls from App Engine Tests to find hot tests.
  * TestTimerPlugin: Adds timing for individual tests and lets you sort the output.
  * XmlOutputPlugin: Allows output of formatted XML reports
  
Usage
=====

Adds vrs_nose_plugins project base to your path.  Import plugins you want to use:

    import vrs_nose_plugins.gae_rpc_counter
    
That is all there is to it.

