# ua-tts-bench

A benchmark of Ukrainian text-to-speech models. This repository contains one adapter script for each model. Each script generates audio for the dataset, computes the metrics and makes MP3 copies. It uses the [`ua-tts-eval`](https://github.com/maksym-halych/ua-tts-eval) package.

The results go to the `ua-tts-bench` dataset on Hugging Face. The [`ua-tts-arena`](https://github.com/maksym-halych/ua-tts-arena) application uses this audio for the human votes.

## Models

| Model     | Script                          | Package           |
| --------- | ------------------------------- | ----------------- |
| holos     | `scripts/evaluate_holos.py`     | `holos-tts==0.4`  |
| omnivoice | `scripts/evaluate_omnivoice.py` | `omnivoice==0.2.1` |

## Folder layout

The three repositories must be in the same folder:

```
ua-tts-benchmark/
├── ua-tts-eval/
├── ua-tts-bench/
│   ├── scripts/
│   └── .cache/ua-tts-eval/     the results, one folder per model
└── ua-tts-arena/
```

Each script gets `ua-tts-eval` from `../ua-tts-eval`.

## Requirements

| Item                                     | Use                                                    |
| ---------------------------------------- | ------------------------------------------------------ |
| [uv](https://docs.astral.sh/uv/)         | Installs the packages of each script and runs it.      |
| `ffmpeg` on `PATH`                       | Makes the MP3 copies.                                  |
| An ASR server with the OpenAI API        | Makes the transcripts for WER and CER. The scripts use `http://127.0.0.1:5092/v1`. |

## Run a model

1. Start the ASR server.
2. In the `ua-tts-bench` folder, run the script of the model:

   ```bash
   uv run scripts/evaluate_holos.py
   ```

3. Read `.cache/ua-tts-eval/holos/bench.log`. Make sure that no item failed.

The script deletes the existing folder of the model before it starts.

> **Caution:** Do not run the script again for a model that has votes in the arena. The votes refer to the current audio. If you must change the audio, give the model a new name, for example `holos-2`.

## Add a model

1. Copy a script in `scripts/` and change the name to `evaluate_<model>.py`.
2. In the script, write a subclass of `TtsModel`. Set `name`, `device` and `params`, and write `synthesize`.
3. Add the packages of the model to the `dependencies` list at the top of the script. Use exact versions.
4. Commit the script before you run it. The manifest records the commit of this repository.
5. Run the script. See [Run a model](#run-a-model).
6. Upload the folder to Hugging Face:

   ```bash
   hf upload <user>/ua-tts-bench .cache/ua-tts-eval/<model> <model> --repo-type dataset
   ```

7. Add the model on the **Models** page of the arena.

## Results

The `ua-tts-eval` design document describes the files in a model folder.

## License

MIT. See `LICENSE`.
