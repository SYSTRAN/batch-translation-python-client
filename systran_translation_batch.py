#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import argparse
import time
import mimetypes

# to resolve problem with SSL warning for python earlier than 2.7.9
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# import translation-api-python-client (version >= 1.0.0) and gateway version >= 0.0.27
import systranTranslationApi
import systranTranslationApi.configuration

parser = argparse.ArgumentParser(description="a script to translate all files of a directory")
parser.add_argument("-k", "--keyfile" , required=True, help="API key file")
parser.add_argument("-s", "--source" , required=False, help="source language")
parser.add_argument("-t", "--target" , required=True, help="target language")
parser.add_argument("-i", "--input" , required=True, help="input directory")
parser.add_argument("-o", "--output" , required=True, help="output directory where translated documents are stored")
parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
parser.add_argument("--interval" , type=int, help="interval between checks of finished translations (in seconds)", default=10)

args = parser.parse_args()

if not os.path.isdir(args.input):
    sys.exit("the input argument must be a directory path")
inputDir = os.path.realpath(args.input)

if not os.path.lexists(args.output):
    os.makedirs(args.output) # if output directory doesn't exist, create it
elif not os.path.isdir(args.output):
    sys.exit("the output argument must be a directory path")
outputDir = os.path.realpath(args.output)

if inputDir == outputDir:
    sys.exit("input and output directories must be different")

api_key_file = os.path.realpath(args.keyfile)
systranTranslationApi.configuration.load_api_key(api_key_file)
translation_api = systranTranslationApi.TranslationApi(systranTranslationApi.ApiClient())

# create a batch to do some translations
try:
    batch = translation_api.translation_file_batch_create_get()
except Exception as e:
    print "Cannot create batch: ", e
    sys.exit(1)
batch_id = batch.batch_id
print "Batch %s created" % batch_id

print "Sending translation requests"
requestMap = {}
for inputFile in os.listdir(inputDir):
    inputFilePath = os.path.join(inputDir, inputFile)
    if os.path.isfile(inputFilePath):
        try:
            if args.source != None:
                result = translation_api.translation_file_translate_get(source=args.source,target=args.target, input=inputFilePath, async=True, with_source=False, with_annotations=False, batch_id=batch_id)
            else:
                result = translation_api.translation_file_translate_get(target=args.target, input=inputFilePath, async=True, with_source=False, with_annotations=False, batch_id=batch_id)
        except Exception as e:
            print "Cannot send request for file %s: %s" % (inputFile, e)
        else:
            requestMap[result.request_id] = inputFile
            if args.verbose:
                print "add to batch %s as request %s" % (inputFile, result.request_id)

# close the batch
try:
    batch_close = translation_api.translation_file_batch_close_get(batch_id = batch_id)
except Exception as e:
    print "Cannot close batch %s: %s" % (batch_id, e)
else:
    print "Batch %s closed" % batch_id

print "All translation requests have been sent. Each translation will be stored in directory %s when they will be avaiable" % outputDir

# check batch status and store request result when it is avaiable
while requestMap:
    if args.verbose:
        print "Waiting for %d results" % len(requestMap)
    time.sleep(args.interval)
    batch_status = translation_api.translation_file_batch_status_get(batch_id=batch_id)
    for request in batch_status.requests:
        if request.status != "pending":
            if request.id in requestMap:
                if request.status == "error":
                    status = translation_api.translation_file_status_get(request_id=request.id)
                    print "final state for request %s: %s (%s)" % (request.id, request.status, status.description)
                elif request.status == "finished":
                    # make the ouput file name
                    outputFilename = requestMap[request.id]
                    mimetype, encoding = mimetypes.guess_type(outputFilename) # this method use the extension file to know the mime type
                    if mimetype == "application/pdf":
                        outputFilename += ".mht"
                    outputFilePath = os.path.join(outputDir, outputFilename)

                    # retrieve translation result and store it in the ouput file
                    try:
                        result = translation_api.translation_file_result_get(request_id=request.id)
                        print "request %s finished. Writing result in file %s" % (request.id, outputFilePath)
                        f = open(outputFilePath, "wb")
                        f.write(result["output"])
                        f.close()
                    except Exception as e:
                        print "Cannot retrieve result for file %s and request %s: %s" % (requestMap[request.id], request.id, e)
                else:
                    print "final state for request %s: %s" % (request.id, request.status)
                del requestMap[request.id] # remove the request to not treat twice (and stop the while loop)
