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
import struct
import sys
import xpng
import os.path



# A named tuple representing a fingerprint test
# name = name of the test
# filename = filename of the png file to test
# function = function to call to execute the test
# description = description of the test
Test = namedtuple("test", "name filename function description")

# A named tuple representing the fingerprint of a PNG library
# name = name of the language / library / tool
# description = description of the library (e.g. version number)
# results = a dictionary of test fingerprint test results
Fingerprint = namedtuple("fingerprint", "name description results")


###############################################
#
# Fingerprinting functions
#
###############################################


# The most simple fingerprinting function
#
# Returns 0 if the image is absent or empty (meaning the target failed to decode the input image)
# Returns 10 if the image looks valid at least in surface
# Returns between 1 and 9 if the image is corrupt
def conversionSuccess(image):
    return image.valid


# All the following tests should return values > 10 (or any kind of object like a list actually)
################################################################################################

# Fingerprint depending on the correctness of the checksums of the output image
def correctChecksums(image):
    if image._verify_checksums():
        return 11
    else:
        return 12


# Fingerprint resulting from the set of filters used in the scanlines of the output image (returns a sorted list of the filters)
def filtersUsed(image):
    return sorted(image.filters_used)


# Fingerprint depending on the palette used to decode images with two palettes (when not rejected)
def paletteUsed(image):
    if image.hasColor([185, 96, 142]):
        return 11
    elif image.hasColor([96, 142, 185]):
        return 12
    else:
        return 13


# Fingerprint depending on how the decoder treated the gamma information from the input image
def gamma(image):
    pixel = image.getPixelRgb(120, 140)
    if pixel[0] + pixel[1] + pixel[2] < 96:
        return 11
    else:
        chunk = image._get_chunk("gAMA")
        if chunk == None:
            return 12
        gammav = struct.unpack("!I", chunk.content)
        if gammav[0] == 400000:
            return 13
        return 14


# Fingerprint depending on the ihdr used to decode images with two ihdr (when not rejected)
def ihdrUsed(image):
    if image.width == 252:
        return 11
    elif image.width == 189:
        return 12
    else:
        return 13


# Fingerprint depending on the treatment of images with invalid scanline filters
def badIdatFilter(image):
    pixel = image.getPixelRgb(5, 0)
    if pixel == [65, 83, 255]:
        return 11  # Most libraries return the correct image
    elif pixel == [57, 82, 255]:
        return 12  # One library outputs a corrupted image
    return 13


# Fingerprint depending on the zlib compression level flag of the output image
def zlibCompression(image):
    return 11 + image.zlevel


# Fingerprint depending on how the decoder treated the phys information in the input image
def physChunk(image):
    chunk = image._get_chunk("pHYs")
    if chunk == None:
        return 11
    x, y, u = struct.unpack("!IIB", chunk.content)
    if x == 1:
        return 12
    if x == 1500:
        return 13
    if x == 1499:
        return 14  # .net
    return 15


# Fingerprint depending on how the decoder treated an input image with a tRNS chunk
def truecolorTrns(image):
    if image.colorType == 6:
        return 11
    chunk = image._get_chunk("tRNS")
    if chunk == None:
        return 12
    return 13


###############################################

# include all the tests and fingerprints from external files

execfile("tests.py")
execfile("fingerprints.py")


###############################################


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
        image = xpng.Png(content)
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
tests = sorted([t for t in locals.itervalues() if isinstance(t, Test)], key=operator.attrgetter('name'))
fingerprints = [t for t in locals.itervalues() if isinstance(t, Fingerprint)]

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
