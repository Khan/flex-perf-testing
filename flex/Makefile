clean:
	rm *.pyc

run:
	echo COPY AND PASTE THE STATEMENTS BELOW, doesnt work by itself sorry
	export GOOGLE_APPLICATION_CREDENTIALS=./khan-cachetest-4e33955967d6.json
	export DATASTORE_DATASET=khan-cachetest
	export DATASTORE_EMULATOR_HOST=localhost:8081
	export DATASTORE_EMULATOR_HOST_PATH=localhost:8081/datastore
	export DATASTORE_HOST=http://localhost:8081
	export DATASTORE_PROJECT_ID=khan-cachetest
db:
	gcloud beta emulators datastore start --project=khan-cachetest
