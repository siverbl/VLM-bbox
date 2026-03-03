from __future__ import annotations

import argparse
import statistics
import time

import requests


def percentile(values, p):
    idx = int(round((len(values) - 1) * p))
    return sorted(values)[idx]


def run(url: str, image: str, query: str, runs: int, warmup: int):
    for _ in range(warmup):
        with open(image, "rb") as f:
            requests.post(url, files={"file": f}, data={"query": query}, timeout=30)

    latencies_ms = []
    for _ in range(runs):
        start = time.perf_counter_ns()
        with open(image, "rb") as f:
            r = requests.post(url, files={"file": f}, data={"query": query}, timeout=30)
        end = time.perf_counter_ns()
        r.raise_for_status()
        latencies_ms.append((end - start) / 1_000_000)

    print(f"median_ms={statistics.median(latencies_ms):.2f}")
    print(f"p90_ms={percentile(latencies_ms, 0.90):.2f}")
    print(f"p99_ms={percentile(latencies_ms, 0.99):.2f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8000/bbox")
    p.add_argument("--image", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--runs", type=int, default=50)
    p.add_argument("--warmup", type=int, default=5)
    args = p.parse_args()
    run(args.url, args.image, args.query, args.runs, args.warmup)
