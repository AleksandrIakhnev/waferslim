waferslim
=========

|Build Status|

FitNesse SLIM protocol v0.3 implementation compatible with python 3.2+

This is a fork of peterdemin_ 's fork.


Quickstart
----------

#. Download Fitnesse_
#. In the same directory, run ``git clone https://github.com/magmax/waferslim.git``
#. Run Fitnesse_: ``java -jar fitnesse-standalone.jar -p 9000``
#. Create a new *wiki* with this content:

   .. code:: text

      !define TEST_SYSTEM {slim}

      !path .:fixtures
      !define COMMAND_PATTERN {python -m waferslim.server -s %p -p }

      |Import|
      |my_fixture.py|

      |MyClass|
      |arg_1|arg_2|test?|
      |1|1|true|
      |1|0|true|

#. Write ``fixtures/my_fixture.py``:

   .. code:: python

      class MyClass(object):
          arg_1 = None
          arg_2 = None

          def setArg_1(self, value):
             self.arg_1 = value

          def setArg_2(self, value):
             self.arg_2 = value

          def test(self):
             // whatever; i.e.: compare arguments
             return self.arg_1 == arg_2

#. Run tests

More information about `using Fitnesse with Python`_ (Spanish)


.. |Build Status| image:: https://travis-ci.org/magmax/waferslim.png
   :target: https://travis-ci.org/magmax/waferslim
   :alt: Build Status

.. _`Fitnesse`: http://www.fitnesse.org/
.. _`using Fitnesse with Python`: http://magmax.org/blog/tests-de-aceptacion-con-fitnesse/
.. _`peterdemin`: https://github.com/peterdemin/waferslim
