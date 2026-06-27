import argparse
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from pipeline.run_video import run_video_pipeline
except ModuleNotFoundError:
    from run_video import run_video_pipeline


ROOT_DIR = Path(__file__).resolve().parents[1]

PIPELINE_STEPS = {
    "scrape": [
        ["python", "scrapers/fundus/scraper.py", "--date"],
        ["python", "scrapers/reddit/scraper.py"],
    ],
    "cards": [
        ["python", "card/event/process.py", "--date"],
        ["python", "card/statement/process.py", "--date"],
    ],
    "cluster": [
        ["python", "cluster/group_content.py", "--date"],
        ["python", "cluster/regroup_with_size_limits.py", "--date"],
    ],
    "generate": [
        ["python", "generate_article/generate_article.py", "--date"],
        ["python", "generate_article/gather_resource.py", "--date"],
        ["python", "generate_article/category_arrange.py", "--date"],
    ],
    "audio": [
        ["python", "deployment/audio/main.py", "--date"],
    ],
    "image": [
        ["python", "deployment/image/main.py", "--date"],
    ],
    "summary": [
        ["python", "deployment/summary/generate_summary.py", "--date"],
        [
            "python",
            "deployment/audio/tts.py",
            "--speech",
            "deployment/summary/resource/summary.txt",
            "--output",
            "deployment/summary/resource/summary.mp3",
            "--voice",
            "us",
        ],
    ],
    "migrate": [
        ["python", "migrate.py", "--date"],
    ],
    "evaluate": [
        ["python", "evaluate/evaluate.py", "--date"],
    ],
    "knowledge-graph": [
        ["python", "data/output/generate_kg.py"],
    ],
}

DEFAULT_STEPS = ["scrape", "cards", "cluster", "generate", "audio", "image", "summary"]


def expand_command(command: list[str], date: str) -> list[str]:
    expanded = []
    for item in command:
        expanded.append(item)
        if item == "--date":
            expanded.append(date)
    return expanded


def run_command(command: list[str]) -> None:
    command_text = " ".join(command)
    print(f"Running: {command_text}")
    subprocess.run(command, cwd=ROOT_DIR, check=True)


def parse_steps(raw_steps: str) -> list[str]:
    if raw_steps == "default":
        return DEFAULT_STEPS
    if raw_steps == "all":
        return list(PIPELINE_STEPS.keys())

    steps = [step.strip() for step in raw_steps.split(",") if step.strip()]
    unknown_steps = [step for step in steps if step not in PIPELINE_STEPS]
    if unknown_steps:
        raise ValueError(
            "Unknown pipeline step(s): "
            + ", ".join(unknown_steps)
            + ". Available steps: "
            + ", ".join(PIPELINE_STEPS.keys())
        )
    return steps


def run_pipeline(date: str, steps: list[str], include_video: bool = False) -> None:
    print(f"Process date: {date}")
    print(f"Pipeline steps: {', '.join(steps)}")

    for step in steps:
        print(f"\nStep: {step}")
        for command in PIPELINE_STEPS[step]:
            run_command(expand_command(command, date))

    if include_video:
        print("\nStep: video")
        run_video_pipeline(date=date)

    print(f"\nPipeline completed at {datetime.now().isoformat(timespec='seconds')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the LLM-NewsHub data pipeline.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument(
        "--steps",
        default="default",
        help=(
            "Comma-separated steps to run. Use 'default' for the main pipeline or 'all' "
            "for all non-video steps. Available steps: "
            + ", ".join(PIPELINE_STEPS.keys())
        ),
    )
    parser.add_argument(
        "--include-video",
        action="store_true",
        help="Run the optional Wav2Lip video pipeline after the selected steps.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    steps = parse_steps(args.steps)
    run_pipeline(date=args.date, steps=steps, include_video=args.include_video)


if __name__ == "__main__":
    main()
