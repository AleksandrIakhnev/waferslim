''' Example of a Slim LibraryTable -- 
based on http://fitnesse.org/FitNesse.UserGuide.SliM.LibraryTable

Fitnesse table markup:

|import|
|waferslim.examples.library|

|library|
|file support|

|script|my fixture|
|do business logic|/tmp|
|delete|/tmp|

'''

import logging


class FileSupport():
    ''' A class to use as a library '''
    def delete(self, folder):
        ''' Delete some folder here... '''
        pass
    
class MyFixture():
    ''' A class that can be combined with a library in a test ''' 
    def do_business_logic(self, folder):
        ''' Do some business logic here... '''
        pass


class Eval():
    def do_eval(self,params):
        logging.info("Do eval wit params %s", params)