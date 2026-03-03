from __future__ import annotations

import argparse

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/bbox")
    parser.add_argument("--image", required=True)
    parser.add_argument("--query", required=True)
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        resp = requests.post(args.url, files={"file": f}, data={"query": args.query}, timeout=30)

    print(resp.text)


if __name__ == "__main__":
    main()
