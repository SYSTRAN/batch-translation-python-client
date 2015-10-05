# batch-translation-python-client
Batch translation example using systran/translation-api-python-client

## details
systran_translation_batch.py : launch a batch to translate all files from a directory and store the translation in an ouput directory
batch_status.py : take a batch ID as parameter and print a summary of the status

## how to use
1. download systran/translation-api-python-client on github (version >= 1.0.0)
2. add translation-api-python-client to the environment variable PYTHONPATH
3. create a file with your API key (e.g. echo "16d4c575-4606-48cd-afa2-486d4a01ad51" > my_api_key.txt)
4. launch script with --help option for more information
