import os
import zipfile
from common.resources import gen_audio_job, clips_bucket, models_bucket, model_dir, zip_path
from nitric.context import JobContext
from nitric.application import Nitric
from transformers import AutoProcessor, BarkModel

import scipy
import io
import torch
import numpy as np
import requests

clips = clips_bucket.allow("write")
models = models_bucket.allow("read")

# This defines the Job Handler that will process all audio generation jobs
# using the job definition we created in the resources module
@gen_audio_job(cpus=4, memory=12000, gpus=0)
async def do_generate_audio(ctx: JobContext):
    # The name of the file to save the audio to
    file = ctx.req.data["file"]
    # The text to convert to audio
    text: str = ctx.req.data["text"]
    voice_preset: str = ctx.req.data["preset"]
    model_id = ctx.req.data["model_id"]

    # Copy model from nitric bucket to local storage
    if not os.path.exists(model_dir):
        print("Downloading model")
        download_url = await models.file(f"{model_id}.zip").download_url()
        response = requests.get(download_url, allow_redirects=True, timeout=600)

        # make sure zip_path exists
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        # Save zip file
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print("unzipping model")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)

        # clean up
        os.remove(zip_path)

    print("Loading model")
    model = BarkModel.from_pretrained(model_dir)
    processor = AutoProcessor.from_pretrained(model_dir)
    print("Model loaded")

    # Split the text by sentences and chain the audio clips together
    # We do this because the model can only reliably generate a small amount of audio at a time
    sentences = text.split(".")
    sentences = [sentence for sentence in sentences if sentence.strip() != ""]

    audio_arrays = []
    # generate an audio clip for each sentence
    for index, sentence in enumerate(sentences):
        # "..." inserts pauses between sentences to prevent clips from running together
        inputs = processor(f"{sentence}...", voice_preset=voice_preset)

        # Move the inputs and model to the GPU if available
        if torch.cuda.is_available():
            inputs.to("cuda")
            model.to("cuda")
        else:
            print("CUDA unavailable, defaulting to CPU. This may take a while.")

        print(f"Generating clip {index + 1}/{len(sentences)}")
        audio_array = model.generate(**inputs, pad_token_id=0)
        audio_array = audio_array.cpu().numpy().squeeze()

        audio_arrays.append(audio_array)

    # Concatenate the audio clips together
    final_array = np.concatenate(audio_arrays)

    buffer = io.BytesIO()
    print("Encoding clip")
    sample_rate = model.generation_config.sample_rate
    scipy.io.wavfile.write(buffer, rate=sample_rate, data=final_array)

    print("Storing the audio to the clips bucket")
    upload_url = await clips.file(f'{file}.wav').upload_url()
    requests.put(upload_url, data=buffer.getvalue(), headers={"Content-Type": "audio/wav"}, timeout=600)

    print("Done!")

Nitric.run()