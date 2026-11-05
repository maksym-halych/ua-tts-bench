#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "omnivoice==0.2.1",
#     "ua-tts-eval",
# ]
#
# [tool.uv.sources]
# ua-tts-eval = { path = "../../ua-tts-eval", editable = true }
# ///
"""Generate and evaluate OmniVoice. Run from the repo root: uv run scripts/evaluate_omnivoice.py"""

import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from ua_tts_eval import TtsModel, evaluate, export_mp3, generate

ASR_BASE_URL = "http://127.0.0.1:5092/v1"
ASR_MODEL = "parakeet-tdt-0.6b-v3"


class OmniVoiceTtsModel(TtsModel):
    name = "omnivoice"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    params = {
        "package": "omnivoice==0.2.1",
        "checkpoint": "k2-fsa/OmniVoice",
        "revision": "c5fdb5ccb189668d56333f77ba2629f4cd7535f4",
        "language": "uk",
        "voice": "auto",
        "seed": 1234,
    }

    def __init__(self):
        checkpoint = snapshot_download(self.params["checkpoint"], revision=self.params["revision"])
        self.model = OmniVoice.from_pretrained(checkpoint, device_map=self.device, dtype=torch.float16)

    def synthesize(self, text):
        # Sampling is random, so each item gets the same seed to make the run repeatable.
        torch.manual_seed(self.params["seed"])
        audio = self.model.generate(text=text, language=self.params["language"])
        return audio[0], self.model.sampling_rate


if __name__ == "__main__":
    folder = generate(OmniVoiceTtsModel())
    evaluate(folder, asr_base_url=ASR_BASE_URL, asr_model=ASR_MODEL)
    export_mp3(folder)
