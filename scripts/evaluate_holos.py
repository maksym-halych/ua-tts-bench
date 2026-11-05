#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "holos-tts==0.4",
#     "ipa-uk",
#     "ua-tts-eval",
#     "ukrainian-word-stress",
# ]
#
# [tool.uv.sources]
# ipa-uk = { git = "https://github.com/patriotyk/ipa-uk.git", rev = "3faf05ec50fd4880965b6c76f8e479a4f82117f5" }
# ua-tts-eval = { path = "../../ua-tts-eval", editable = true }
# ukrainian-word-stress = { git = "https://github.com/patriotyk/ukrainian-word-stress.git", rev = "d5b37ea0abe9711930d9c3b0b13edec5a0675512" }
# ///
"""Generate and evaluate HolosTTS. Run from the repo root: uv run scripts/evaluate_holos.py"""

import re
import unicodedata

import numpy as np
import torch
from holos.models import HolosTTS
from ipa_uk import ipa
from ua_tts_eval import TtsModel, evaluate, export_mp3, generate
from ukrainian_word_stress import Stressifier

ASR_BASE_URL = "http://127.0.0.1:5092/v1"
ASR_MODEL = "parakeet-tdt-0.6b-v3"
SENTENCE_END = re.compile(r"(?<=[.?!:])\s+")
DASHES = re.compile(r"[᠆‐‑‒–—―⁻₋−⸺⸻]")


class HolosTtsModel(TtsModel):
    name = "holos"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    params = {"package": "holos-tts==0.4", "checkpoint": "patriotyk/HolosTTS", "speed": 1.0}

    def __init__(self):
        self.model = HolosTTS(self.params["checkpoint"], device=self.device)
        self.stressify = Stressifier()
        self.params = {**self.params, "voice": self.model.list_voices()[0]}

    def _phonemes(self, sentence: str) -> str:
        # The same steps as the text frontend of the HolosTTS demo app.
        sentence = DASHES.sub("-", unicodedata.normalize("NFKC", sentence).replace('"', ""))
        if sentence[-1] not in ".?!:-":
            sentence += "."
        return ipa(self.stressify(sentence.replace(" - ", ": ")))

    def synthesize(self, text):
        # The model is meant to get one sentence at a time.
        phonemes = [self._phonemes(sentence) for sentence in SENTENCE_END.split(text.strip())]
        parts = [
            self.model.generate(sentence, self.params["voice"], speed=self.params["speed"]).squeeze().cpu().numpy()
            for sentence in phonemes
            if sentence
        ]
        return np.concatenate(parts), 24000


if __name__ == "__main__":
    folder = generate(HolosTtsModel())
    evaluate(folder, asr_base_url=ASR_BASE_URL, asr_model=ASR_MODEL)
    export_mp3(folder)
