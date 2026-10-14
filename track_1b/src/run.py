#!/usr/bin/env python3

import argparse
import os
import platform
import sys

import httpx


REQUIRED_ENV_VARS = (
    "LLM_NAME",
    "LLM_BASE_URL",
    "LLM_API_KEY",
)


def get_config() -> dict[str, str]:
    return {
        name: os.getenv(name, "").strip()
        for name in REQUIRED_ENV_VARS
    }


def validate_config(config: dict[str, str]) -> list[str]:
    return [
        name
        for name in REQUIRED_ENV_VARS
        if not config.get(name)
    ]


def check_runtime() -> int:
    print("Apertus Swiss HVET Eval")
    print(f"Python: {platform.python_version()}")
    print("Runtime check: OK")
    return 0


def check_config() -> int:
    config = get_config()
    missing = validate_config(config)

    print("Apertus Swiss HVET Eval")
    print(f"LLM_NAME: {config['LLM_NAME'] or '[not set]'}")
    print(f"LLM_BASE_URL: {config['LLM_BASE_URL'] or '[not set]'}")
    print(
        "LLM_API_KEY: "
        + ("[configured]" if config["LLM_API_KEY"] else "[not set]")
    )

    if missing:
        print(
            "Missing required environment variables: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    print("Configuration check: OK")
    return 0


def api_smoke() -> int:
    config = get_config()
    missing = validate_config(config)

    if missing:
        print(
            "Missing required environment variables: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 2

    endpoint = (
        config["LLM_BASE_URL"].rstrip("/")
        + "/chat/completions"
    )

    payload = {
        "model": config["LLM_NAME"],
        "messages": [
            {
                "role": "user",
                "content": "Antworte mit genau dem Wort OK.",
            }
        ],
        "temperature": 0,
        "max_tokens": 16,
    }

    headers = {
        "Authorization": f"Bearer {config['LLM_API_KEY']}",
        "Content-Type": "application/json",
    }

    print("Apertus Swiss HVET Eval")
    print(f"Model: {config['LLM_NAME']}")
    print(f"Endpoint: {endpoint}")
    print("Sending one API smoke-test request...")

    try:
        with httpx.Client(
            timeout=60.0,
            follow_redirects=True,
        ) as client:
            response = client.post(
                endpoint,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

    except httpx.HTTPStatusError as exc:
        print(
            f"HTTP error: {exc.response.status_code}",
            file=sys.stderr,
        )
        print(
            exc.response.text[:1000],
            file=sys.stderr,
        )
        return 3

    except httpx.HTTPError as exc:
        print(
            f"Connection error: {exc}",
            file=sys.stderr,
        )
        return 4

    except ValueError:
        print(
            "API returned invalid JSON.",
            file=sys.stderr,
        )
        return 5

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        print(
            "Unexpected API response structure.",
            file=sys.stderr,
        )
        print(str(data)[:1000], file=sys.stderr)
        return 6

    print(f"Response: {content!r}")
    print("API smoke test: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reproducible evaluation runner "
            "for Apertus Swiss HVET Eval."
        )
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
        help=(
            "Verify required LLM configuration "
            "without making an API request."
        ),
    )

    group.add_argument(
        "--api-smoke",
        action="store_true",
        help="Send exactly one test request to the configured LLM.",
    )

    args = parser.parse_args()

    if args.check_runtime:
        return check_runtime()

    if args.api_smoke:
        return api_smoke()

    return check_config()


if __name__ == "__main__":
    sys.exit(main())
