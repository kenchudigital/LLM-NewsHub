# Requirements Guide

The project keeps separate dependency files because different parts of the system have different runtime needs.

## Files

```text
requirements.txt                 # Root install entrypoint; points to requirements/pipeline.txt
requirements/pipeline.txt        # Main data, ML, scraping, LLM, image, and audio pipeline
requirements/wav2lip.txt         # Optional Wav2Lip/video environment
requirements/full-freeze.txt     # Original full environment freeze for development history
apps/requirements.txt            # FastAPI backend dependencies used by apps/Dockerfile
evaluate/requirements.txt        # Evaluation-only dependencies
```

## Recommended Setup

Main pipeline:

```bash
conda create -n llm-news python=3.10
conda activate llm-news
pip install -r requirements.txt
python setup_nltk.py
```

Optional Wav2Lip/video pipeline:

```bash
conda create -n llm-news-video python=3.8
conda activate llm-news-video
pip install -r requirements/wav2lip.txt
```

## Why Not Merge Everything?

The original `requirements/full-freeze.txt` contains a complete local environment export, including platform-specific `file://` package references. It is useful as a development record, but it is not a good public install file.

The Wav2Lip/video stack also has different Python and media dependency requirements. Keeping it separate avoids forcing every user to install the heavier optional video stack just to run the main news pipeline or web demo.
