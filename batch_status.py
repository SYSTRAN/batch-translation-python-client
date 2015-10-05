#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

import argparse

# to resolve problem with SSL warning for python earlier than 2.7.9
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

# import translation-api-python-client (version >= 1.0.0) and gateway version >= 0.0.27
import systranTranslationApi
import systranTranslationApi.configuration

parser = argparse.ArgumentParser(description="give a summary of a batch status")
parser.add_argument("-k", "--keyfile" , required=True, help="API key file")
parser.add_argument("-i", "--id" , required=True, help="batch id")

args = parser.parse_args()

api_key_file = os.path.realpath(args.keyfile)
systranTranslationApi.configuration.load_api_key(api_key_file)
translation_api = systranTranslationApi.TranslationApi(systranTranslationApi.ApiClient())

summary = {"pending":0, "finished":0, "error":0, "cancelled":0}
batch_status = translation_api.translation_file_batch_status_get(batch_id=args.id)
for request in batch_status.requests:
    if request.status == "pending":
        summary["pending"] += 1
    elif request.status == "finished":
        summary["finished"] += 1
    elif request.status == "error":
        summary["error"] += 1
    elif request.status == "cancelled":
        summary["cancelled"] += 1

print summary
