# LLM-NewsHub

LLM-NewsHub is a university project that explores an end-to-end AI news workflow: scraping news and social media content, extracting structured event cards, grouping related stories, generating articles with LLMs, creating multimedia summaries, and presenting the result in a web application.

The repository is intentionally kept as a development journey as well as a showcase. The main pipeline is documented clearly, while experimental work such as Airflow, cloud deployment, and multimedia generation remains available as part of the project learning trail.

## Demo

- Project introduction video: [YouTube](https://youtu.be/KjqQ_xPuOYQ)
- Quick start guide: [quick_start.md](quick_start.md)
- Technical report and model notes: [report.md](report.md)

![Demo](source/demo.gif)

## Table of Contents

- [Project Highlights](#project-highlights)
- [System Pipeline](#system-pipeline)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Optional Advanced Components](#optional-advanced-components)
- [Development Notes](#development-notes)
- [Environment](#environment)
- [License](#license)

## Project Highlights

- Collects news articles and social media signals from multiple sources.
- Converts raw content into structured event cards and statement cards.
- Uses category classification, fake news detection, sentiment features, and publisher trust signals.
- Groups related news with TF-IDF and K-Means clustering.
- Generates article content, supporting resources, audio summaries, images, and optional lip-sync videos.
- Serves the generated result through a React frontend and FastAPI backend.
- Includes experiment notes for Airflow orchestration, cloud deployment, evaluation, and knowledge graph interaction.

## System Pipeline

```text
Scraping
  -> Event / Statement Card Generation
  -> Classification and Clustering
  -> LLM Article Generation
  -> Image / Audio / Summary Generation
  -> Optional Wav2Lip Video Generation
  -> Migration to Web App Static Assets
  -> React + FastAPI Showcase UI
```

The clearer pipeline entrypoints are:

```bash
# Main data and media pipeline
python pipeline/run.py --date "2025-06-21"

# Main pipeline plus optional Wav2Lip video step
python pipeline/run.py --date "2025-06-21" --include-video

# Optional video step only
python pipeline/run_video.py --date "2025-06-21"
```

The old commands are still supported for compatibility:

```bash
python run_all.py --date "2025-06-21"
python run_video_only.py --date "2025-06-21"
```

## Repository Structure

```text
LLM-NewsHub/
├── apps/                  # React frontend, FastAPI backend, Docker setup
├── scrapers/              # News, Reddit, and trust-score scraping
├── card/                  # Event and statement card extraction
├── classifier/            # Category classifier and fake news detector
├── cluster/               # Content grouping and regrouping
├── generate_article/      # LLM article generation and resource gathering
├── deployment/            # Image, audio, summary, and Wav2Lip integration
├── evaluate/              # Generated content evaluation
├── data/                  # Data schemas, outputs, and knowledge graph work
├── pipeline/              # Clear pipeline entrypoints
├── infrastructure/        # Airflow and cloud deployment experiments
├── requirements/          # Environment-specific dependency files
├── quick_start.md         # Detailed run commands
└── report.md              # Project methodology and model notes
```

## Quick Start

Install the Python dependencies and prepare NLTK data:

```bash
make setup
```

Run the web application:

```bash
cd apps
docker compose up
```

Run the main pipeline:

```bash
conda activate llm-news
python pipeline/run.py --date "2025-06-21"
```

Copy generated data into the web app:

```bash
python migrate.py --date "2025-06-21"
```

For detailed commands, see [quick_start.md](quick_start.md).

## Optional Advanced Components

### Wav2Lip Video Generation

Wav2Lip is managed as an optional third-party dependency through Git submodule setup. It requires a separate Python environment because the media stack has different package requirements from the main project.

```bash
git submodule update --init --recursive
conda create -n llm-news-video python=3.8
conda activate llm-news-video
pip install -r requirements/wav2lip.txt
```

Then run:

```bash
conda activate llm-news-video
python pipeline/run_video.py --date "2025-06-21"
```

### Airflow and Cloud Deployment

`infrastructure/airflow-demo/` and `infrastructure/alibaba-cloud/` are kept as development-process records. They show how orchestration and deployment were explored during the project, but they are not required for the basic demo.

## Development Notes

This repository keeps both the final showcase path and selected development artifacts. The goal is to make the final system understandable while still showing how the project evolved from experiments into a working AI news generation pipeline.

Recommended reading order:

1. Watch the [project video](https://youtu.be/KjqQ_xPuOYQ).
2. Read the pipeline overview in this README.
3. Follow [quick_start.md](quick_start.md) to run the core demo.
4. Read [report.md](report.md) for model decisions, evaluation, and project reasoning.
5. Explore `infrastructure/airflow-demo/` and `infrastructure/alibaba-cloud/` only if you want to see the infrastructure experiments.

## Environment

The project was developed on:

```text
Mac M1 Pro, 16GB RAM, CPU only
Python 3.10.18 for the main pipeline
Python 3.8 for the optional Wav2Lip environment
```

## License

This project is licensed under the MIT License. For details, see [license](license).

## Full Screen Demo

![Full Screen Demo](source/full_screen.png)
