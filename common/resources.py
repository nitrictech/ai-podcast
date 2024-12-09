import os
import tempfile
from nitric.resources import api, bucket, job, topic

# our main API for submitting audio gen jobs
main_api = api("main")

# a job for generating our audio content
gen_audio_job = job("audio")

# a bucket for storing the output audio
clips_bucket = bucket("clips")

# another bucket for storing models
models_bucket = bucket("models")

# use pub/sub to trigger async processing
download_audio_model_topic = topic("download-audio-model")

model_dir = os.path.join(tempfile.gettempdir(), "ai-podcast", ".model")
cache_dir = os.path.join(tempfile.gettempdir(), "ai-podcast", ".cache")
zip_path = os.path.join(tempfile.gettempdir(), "ai-podcast", "model.zip")



