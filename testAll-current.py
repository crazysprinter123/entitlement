######################################################################
#### Program description
######################################################################
"""
Use this program to run all testcases in the /testcases/rhsm/rhsm_gui/ folder.
This program automatically sets up path and runs each test case in succession.
Please make sure all modules are correctly installed before running this.

Modules required for RHEL 7:
ldtp

Make sure assistive technologies is on or else getwindowlist() and get 
applist() will NOT work, even though they seem to work (ie. does not crash). 
Without assistive technologies, getwindowlist and getapplist will not show 
important windows/apps open such as 'subscription-manager-gui' and
mozilla firefox. Since I could not find the assistive technologies button on 
RHEL 7, I used following command in terminal and restart computer:

gsettings set org.gnome.desktop.interface toolkit-accessibility true

This program will run the above command each time to ensure that is on.
"""

"failed"
"""
existing cert -unable to find txtLocation in app map
pools - Not the right available pools are listed!
gui register using rpoxy 
gui subscripe to pool

gui-display-curr
"""



######################################################################
#### To do
######################################################################
"""
-fix autoset python path
-fix check if assist tech is on
"""

######################################################################
#### Main Program
######################################################################

from subprocess import *
import os

if __name__ == "__main__":
  
  cwd = os.getcwd()
  #first turn on assist Tech and set path before we run our test cases
  #print cwd

  assistCmd = "gsettings set org.gnome.desktop.interface toolkit-accessibility true"
  
  call(assistCmd, shell=True)
  print "Assistive technologies ON"
  os.system("./launch.sh")
  print "PATH SET"

  #export PYTHONPATH=$PYTHONPATH:/root/entitlement
    
  #use call function to exceute commands on terminal
  testDirectory = cwd + "/testcases/rhsm/rhsm_gui/Current/"
  failedTests = []
  fileList = os.listdir(testDirectory)
  for file in fileList:
    if file.endswith(".py") and (file not in ["__init__.py", "rhsmguibase.py", "rhsmguilocator.py"]):
      print "**************************************************************"      
      print "TESTING: " + file
      print "**************************************************************\n\n"
      
      #if the test does not succeed, not the best way to do it...but meh.  Revise later    
      try:
        output = check_output("python " + testDirectory + file, stderr=STDOUT, shell=True)      
      except:
      #figure out a way to keep error message!
        failedTests += [file]
        print "FAILED!"
      

      print "FAILED TESTS: " + failedTests
      print
      print
      print "--------------------------------------------------------------"
      print "FINISHED:  " + file
      print "--------------------------------------------------------------\n\n"
  
  for test in failedTests:
    print "TEST FAILED: " + test 
    print
  print str(len(failedTests) * 1.0 /(len(fileList)) * 100.0) + "% of tests failed"
 
  


