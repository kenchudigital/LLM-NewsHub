import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SUMMARY_RESOURCE_DIR = ROOT_DIR / "deployment" / "summary" / "resource"


def run_command(command: list[str], cwd: Path = ROOT_DIR) -> None:
    command_text = " ".join(command)
    print(f"Running: {command_text}")
    subprocess.run(command, cwd=cwd, check=True)


def run_video_pipeline(date: str, skip_wav2lip: bool = False, skip_migrate: bool = False) -> None:
    wav2lip_dir = ROOT_DIR / "deployment" / "Wav2Lip"
    summary_video = SUMMARY_RESOURCE_DIR / "summary.mp4"
    target_dir = ROOT_DIR / "apps" / "static" / "summary-video" / date
    target_video = target_dir / "summary.mp4"

    if not skip_wav2lip:
        inference_script = wav2lip_dir / "inference.py"
        checkpoint = wav2lip_dir / "checkpoints" / "wav2lip_gan.pth"
        face_video = wav2lip_dir / "samples" / "face.mp4"
        summary_audio = SUMMARY_RESOURCE_DIR / "summary.mp3"

        required_files = [inference_script, checkpoint, face_video, summary_audio]
        missing_files = [str(path.relative_to(ROOT_DIR)) for path in required_files if not path.exists()]
        if missing_files:
            raise FileNotFoundError(
                "Missing Wav2Lip inputs: "
                + ", ".join(missing_files)
                + ". See quick_start.md for the optional Wav2Lip setup."
            )

        run_command(
            [
                "python",
                "inference.py",
                "--checkpoint_path",
                "checkpoints/wav2lip_gan.pth",
                "--face",
                "samples/face.mp4",
                "--audio",
                "../summary/resource/summary.mp3",
                "--outfile",
                "../summary/resource/news_report.mp4",
            ],
            cwd=wav2lip_dir,
        )

    run_command(["python", "deployment/summary/merge_video.py"])
    run_command(["python", "deployment/summary/add_bg_music.py"])

    if not summary_video.exists():
        raise FileNotFoundError(f"Summary video was not generated: {summary_video}")

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(summary_video, target_video)
    print(f"Copied summary video to {target_video.relative_to(ROOT_DIR)}")

    if not skip_migrate:
        run_command(["python", "migrate.py", "--date", date])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the optional LLM-NewsHub video pipeline.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument(
        "--skip-wav2lip",
        action="store_true",
        help="Skip Wav2Lip inference and only merge/copy an existing summary video.",
    )
    parser.add_argument(
        "--skip-migrate",
        action="store_true",
        help="Skip copying generated data into the web app static folder.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_video_pipeline(
        date=args.date,
        skip_wav2lip=args.skip_wav2lip,
        skip_migrate=args.skip_migrate,
    )


if __name__ == "__main__":
    main()
