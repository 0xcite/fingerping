#!/usr/bin/python
#
# fingerping: A PNG library fingerprinting tool.
# 
# @author:Dominique Bongard
# 
# Code is licensed under -- Apache License 2.0 http://www.apache.org/licenses/
#

from collections import namedtuple
import operator
import sys
import os.path
from xpng import Xpng
from tests import Tests
from fingerprints import Fingerprints

# Test all the images in a directory (don't print warnings when generating fingerprints)
def doTests(tests, fingerprints, warn):
    results = {}
    fingerprintScores = {}
    # Initialite the count of matching tests to zero for each fingerprint
    for fingerprint in fingerprints:
        fingerprintScores[fingerprint.name] = 0
    # Execute each test
    for test in tests:
        content = readImage(directory + test.filename + ".png")
        image = Xpng(content)
        if not image.valid == 0:
            # Only execute the test if there is an image to test
            result = test.function(image)
        else:
            result = 0
        # Save the result of the test
        results[test.name] = result

        # Check if the result matches some of the fingeprints and if so, increment the match counter
        for fingerprint in fingerprints:
            if not test.name in fingerprint.results:
                # warn if a fingerprint is missing the result for the test being run
                if warn:
                    print "warning, missing key", test.name, "in", fingerprint.name
            elif fingerprint.results[test.name] == result:
                fingerprintScores[fingerprint.name] += 1
    return results, fingerprintScores

# reads the image in memory from file
def readImage(fileName):
    if os.path.exists(fileName):
        with open(fileName, 'rb') as f:
            try:
                return f.read()
            except:
                pass

# Generate a csv table with all the test results for each fingerprint (which you can then import in LibreOffice or whatever)
def generateCsv(tests, fingerprints):
    header = "/"
    for test in tests:
        header = header + "\t" + test.name
    print header

    for fingerprint in fingerprints:
        row = fingerprint.name
        for test in tests:
            if not test.name in fingerprint.results:
                row += "\t\"\""
            else:
                row += "\t" + str(fingerprint.results[test.name])
        print row


# Show the fingerprinting result with the most likely library match at the bottom
def showResults(scores, nb):
    ordered = sorted(scores.iteritems(), key=operator.itemgetter(1))
    for result in ordered:
        print '{:20s} {:3d}/{:3d}'.format(result[0], result[1], nb)


# check if the command line has valid options
def checkCommandLine(line):
    if len(line) == 3:
        if not line[1] == "-gen":
            return False
        else:
            return True
    if len(line) == 2:
        if (line[1][0] == "-") and not (line[1] == "-csv"):
            return False
        return True
    return False


###############################################
#
# Main program
#
###############################################


# use reflection to get all the tests and all the fingeprints in lists
locals = locals().copy()
tests = sorted(Tests.all_tests, key=lambda test: test.name)
fingerprints = Fingerprints.all_fingerprints

if not checkCommandLine(sys.argv):
    print "usage:"
    print ""
    print "fingerping.py path        # Matches the images in the path folder with the fingerprint of known PNG libraries"
    print "fingerping.py -gen path   # Generates a new library fingerprint from the images in the path folder"
    print "fingerping.py -csv        # prints all the known fingerprints as a CSV table"
    sys.exit(0)

# Generate a csv output with all the test results for each library fingerprint known to the tool
if sys.argv[1] == "-csv":
    generateCsv(tests, fingerprints)
    sys.exit(0)

# last command line argument is the directory with all the images to use in a fingerprint test
directory = sys.argv[len(sys.argv) - 1] + "/"

results, fingerprintScores = doTests(tests, fingerprints, sys.argv[1] != "-gen")

# If the -gen parameter is given on the command line, don't give the fingerprinting results
# but instead generate a new fingerprint
if sys.argv[1] == "-gen":
    print results
else:
    showResults(fingerprintScores, len(tests))
