import os
import zipfile

import requests
from common.resources import (
    main_api, gen_audio_job, models_bucket, download_audio_model_topic,
    model_dir, cache_dir, zip_path
)
from nitric.application import Nitric
from nitric.context import HttpContext, MessageContext
from huggingface_hub import snapshot_download

models = models_bucket.allow("write", "read")
download_audio_model = download_audio_model_topic.allow("publish")

# Give this service permission to submit tasks to the gen_audio_job
gen_audio = gen_audio_job.allow("submit")

# See the list of available voice presets at https://suno-ai.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c
default_voice_preset = "v2/en_speaker_6"

audio_model_id = "suno/bark"

@download_audio_model_topic.subscribe()
async def do_download_audio_model(ctx: MessageContext):
    model_id: str = ctx.req.data["model_id"]

    print(f"Downloading model to {model_dir}")

    dir = snapshot_download(model_id,
        local_dir=model_dir,
        cache_dir=cache_dir,
        allow_patterns=[
          "config.json",
          "generation_config.json",
          "pytorch_model.bin",
          "speaker_embeddings_path.json",
          "special_tokens_map.json",
          "tokenizer.json",
          "tokenizer_config.json",
          "vocab.txt"
        ]
    )

    print(f"Downloaded model to {dir}")

    print("Compressing models")

    # zip the model
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zip_file:
        for root, dirs, files in os.walk(dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(file_path, start=dir)
                print(f"Adding {file_path} to zip as {archive_name}")
                zip_file.write(file_path, archive_name)

    # upload the model to the bucket
    model_url = await models.file(f"{model_id}.zip").upload_url()

    with open(zip_path, "rb") as f:
        requests.put(model_url, data=f, timeout=6000)

    os.remove(zip_path)

    print("Successfully cached model in bucket")

@main_api.post("/download-model")
async def download_audio(ctx: HttpContext):
    model_id = ctx.req.query.get("model", audio_model_id)

    if isinstance(model_id, list):
        model_id = model_id[0]

    await download_audio_model.publish({"model_id": model_id})

# Generate a text-to-speech audio clip
@main_api.post("/audio/:filename")
async def submit_auto(ctx: HttpContext):
    name = ctx.req.params["filename"]
    model_id = ctx.req.query.get("model", audio_model_id)
    preset = ctx.req.query.get("preset", default_voice_preset)

    if isinstance(model_id, list):
        model_id = model_id[0]

    model_downloaded = await models.exists(f"{model_id}.zip")
    if not model_downloaded:
        ctx.res.status = 404
        ctx.res.body = f"model {model_id} has not been downloaded yet, call POST: /download-model"
        return
    
    if isinstance(preset, list):
        preset = preset[0]

    body = ctx.req.data
    if body is None:
        ctx.res.status = 400
        return

    # Submit the audio generation job, this will run the job we defined as an async task
    await gen_audio.submit({"file": name, "text": body.decode('utf-8'), "preset": preset, "model_id": model_id})

Nitric.run()