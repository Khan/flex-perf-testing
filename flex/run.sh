#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS=./khan-cachetest-4e33955967d6.json
export DATASTORE_DATASET=khan-cachetest
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_EMULATOR_HOST_PATH=localhost:8081/datastore
export DATASTORE_HOST=http://localhost:8081
export DATASTORE_PROJECT_ID=khan-cachetest
export DATASTORE_USE_PROJECT_ID_AS_APP_ID=true
source env/bin/activate
pip install -r requirements.txt
python main.py
