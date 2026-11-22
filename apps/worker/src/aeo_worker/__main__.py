import argparse
import asyncio

from aeo_worker.runtime import run_worker


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AEO background worker.")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    args = parser.parse_args()
    asyncio.run(run_worker(poll_interval=args.poll_interval))


if __name__ == "__main__":
    main()
