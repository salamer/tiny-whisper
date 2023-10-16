cp -R /app/models* /tmp
mkdir /tmp/models--guillaumekln--faster-whisper-tiny
cp -R /app/models--guillaumekln--faster-whisper-tiny/* /tmp/models--guillaumekln--faster-whisper-tiny/ 
gunicorn -b :8080 -w 1 app:app