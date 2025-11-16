#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import textwrap
from datetime import date

from openai import OpenAI


def get_commits(prev_tag: str | None) -> str:
    """Return `hash summary` commits between prev_tag and HEAD."""
    range_spec = f"{prev_tag}..HEAD" if prev_tag else "HEAD"

    result = subprocess.run(
        ["git", "log", "--pretty=format:%h %s", range_spec],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def build_prompt(version: str, commits: str) -> str:
    if commits:
        commits_block = commits
    else:
        commits_block = (
            "(no new commits - describe the release as a technical update "
            "without notable user-facing changes)"
        )

    return textwrap.dedent(
        f"""
        You are an assistant that writes short yet informative release notes
        for a Python project. Write in English for a developer audience.

        Release version: {version}

        Below is the commit list (latest first). Each commit has a short hash
        and a title:

        {commits_block}

        Response requirements:
        - Produce valid Markdown.
        - Start with 1-3 sentences summarizing the release.
        - Add a `## Changes` section containing a bulleted list.
        - Group related changes logically and avoid repetition.
        - Do not mention commit hashes, authors, or internal IDs.
        - Do not invent changes that are absent from the commits.
        """
    ).strip()


def generate_notes(version: str, prev_tag: str | None) -> str:
    commits = get_commits(prev_tag)
    prompt = build_prompt(version, commits)

    client = OpenAI()

    resp = client.responses.create(
        model="gpt-5.1",
        input=prompt,
    )

    llm_text = resp.output_text.strip()
    header = f"# Version {version} ({date.today().isoformat()})"
    return f"{header}\n\n{llm_text}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--version", required=True)
    _ = parser.add_argument("--prev-tag", default="")
    _ = parser.add_argument("--output", required=True)
    args = parser.parse_args()

    body = generate_notes(args.version, args.prev_tag or None)  # pyright: ignore[reportAny]

    with open(args.output, "w", encoding="utf-8") as f:  # pyright: ignore[reportAny]
        _ = f.write(body)


if __name__ == "__main__":
    main()
