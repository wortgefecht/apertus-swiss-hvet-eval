#!/usr/bin/env python3

import argparse
import os
import platform
import sys


REQUIRED_ENV_VARS = (
    "LLM_NAME",
    "LLM_BASE_URL",
    "LLM_API_KEY",
)


def check_runtime() -> int:
    print("Apertus Swiss HVET Eval")
    print(f"Python: {platform.python_version()}")
    print("Runtime check: OK")
    return 0


def check_config() -> int:
    values = {name: os.getenv(name, "").strip() for name in REQUIRED_ENV_VARS}
    missing = [name for name, value in values.items() if not value]

    print("Apertus Swiss HVET Eval")
    print(f"LLM_NAME: {values['LLM_NAME'] or '[not set]'}")
    print(f"LLM_BASE_URL: {values['LLM_BASE_URL'] or '[not set]'}")
    print(
        "LLM_API_KEY: "
        + ("[configured]" if values["LLM_API_KEY"] else "[not set]")
    )

    if missing:
        print(
            "Missing required environment variables: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    print("Configuration check: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproducible evaluation runner for Apertus Swiss HVET Eval."
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check-runtime",
        action="store_true",
        help="Verify that the container runtime starts correctly.",
    )
    group.add_argument(
        "--check-config",
        action="store_true",
        help="Verify required LLM configuration without making an API request.",
    )

    args = parser.parse_args()

    if args.check_runtime:
        return check_runtime()

    return check_config()


if __name__ == "__main__":
    sys.exit(main())
