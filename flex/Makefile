clean:
	rm *.pyc

run:
	memcached &
	./run.sh

db:
	gcloud beta emulators datastore start --project=khan-cachetest
