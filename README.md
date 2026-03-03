# VLM-bbox (Qwen2-VL-2B-Instruct on Raspberry Pi 5 + Hailo AI Hat+2)

Lowest-latency **offline** object localization service.
Input: image + English object description.  
Output: **exactly** `[x0,y0,x1,y1]`.

## File tree

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── parser.py
│   ├── pipeline.py
│   └── server.py
├── config.yaml
├── requirements.txt
├── scripts/
│   ├── benchmark.py
│   ├── client.py
│   ├── run_server.sh
│   └── setup.sh
├── systemd/
│   └── vlm-bbox.service
└── tests/
    └── test_parser.py
```

---

## Engineering plan (implemented)

### Step 1) Verify platform + versions

```bash
uname -a
cat /etc/os-release
lspci | rg -i hailo
hailortcli fw-control identify
dpkg -l | rg 'hailort|hailo-gen-ai-model-zoo'
python3 --version
```

Expected package versions are exactly `5.2.0` for:
- `hailort`
- `hailort-pcie-driver`
- `hailo_gen_ai_model_zoo`

### Step 2) Install provided 5.2.0 .debs + Python deps

Put files in `./debs/`:
- `hailo_gen_ai_model_zoo_5.2.0_arm64.deb`
- `hailort_5.2.0_arm64.deb`
- `hailort-pcie-driver_5.2.0_all.deb`

Run:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh ./debs .venv
```

Why `dpkg -i` + `apt -f install`: installs local artifacts first, then resolves missing dependencies safely.

### Step 3) Prepare Qwen2-VL-2B-Instruct for Hailo split execution

This project keeps **Qwen2-VL-2B-Instruct** as the only model and uses a split pipeline:

- **NPU (Hailo 10H via HailoRT 5.2.0):** vision encoder HEF (`models/qwen2vl_vision_encoder.hef`).
- **CPU (Pi 5):** language decoding head for bbox text generation.

Use `hailo_gen_ai_model_zoo 5.2.0` to produce/deploy the HEF for Qwen2-VL vision subgraph.
Then place artifacts:

```text
models/
├── Qwen2-VL-2B-Instruct/
└── qwen2vl_vision_encoder.hef
```

### Step 4) Warm server + bbox-only output

- Startup preloads processor/decoder and Hailo runtime.
- Startup executes one dummy inference to warm caches.
- `/bbox` accepts `multipart/form-data` (`file`, `query`) and returns **only** `[x0,y0,x1,y1]`.
- Invalid/not found => `[-1,-1,-1,-1]`.

### Step 5) Benchmark + fastest defaults

Fast preset currently in `config.yaml`:
- `max_image_dim: 512`
- `jpeg_quality: 85`
- `max_new_tokens: 24`
- `temperature: 0.0`
- `top_p: 1.0`
- `batch_size: 1`

Run benchmark:

```bash
source .venv/bin/activate
python scripts/benchmark.py --image samples/test.jpg --query "red mug" --runs 50 --warmup 5
```

Prints median/p90/p99 end-to-end latency.

---

## Run server

```bash
source .venv/bin/activate
uvicorn app.server:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop --http httptools
```

Or latency-focused launcher with CPU pinning:

```bash
BBOX_CPU_CORES=2-5 scripts/run_server.sh
```

## API

### POST `/bbox`
- `multipart/form-data`
  - `file`: image bytes
  - `query`: English text, single target object
- Response body: exactly JSON array of 4 ints
  - e.g. `[32,104,219,380]`
  - or `[-1,-1,-1,-1]`

### curl example

```bash
curl -s -X POST http://127.0.0.1:8000/bbox \
  -F "file=@samples/test.jpg" \
  -F "query=red mug"
```

### Python client

```bash
python scripts/client.py --image samples/test.jpg --query "red mug"
```

---

## Performance knobs

### Image knobs
- `BBOX_MAX_IMAGE_DIM` (`384/448/512/640`): smaller is faster, may reduce localization accuracy.
- `BBOX_JPEG_QUALITY` (`70-95`): lower reduces memory bandwidth + transfer time.

### Decoding knobs
- `BBOX_MAX_NEW_TOKENS`: keep small (`16-32`) for strict short output.
- `BBOX_TEMPERATURE=0.0`
- `BBOX_TOP_P=1.0`
- `BBOX_REPETITION_PENALTY` default `1.0`.

### CPU scheduling knobs
- `BBOX_PREPROCESS_THREADS`
- `BBOX_POSTPROCESS_THREADS`
- Core pinning via `taskset` (`scripts/run_server.sh`).
- Optional priority tuning:
  - `nice -n -5 ...`
  - `chrt -f 20 ...` (careful: can starve system threads).

### Hailo knobs
- Keep `batch_size=1` for latency.
- Ensure low-latency runtime defaults in HailoRT 5.2.0.
- If multiple HEFs are available (different resolutions), switch with:
  - `BBOX_HAILO_HEF_PATH=models/qwen2vl_vision_encoder_448.hef`

---

## Systemd (optional)

```bash
sudo cp systemd/vlm-bbox.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vlm-bbox
sudo systemctl status vlm-bbox
```

---

## Overclocking guidance (optional)

`/boot/firmware/config.txt` example (Pi 5, active cooling required):

```ini
arm_freq=2800
gpu_freq=950
over_voltage_delta=50000
```

Warnings:
- Can cause instability, data corruption, thermal throttling.
- May affect hardware lifespan/warranty.
- Validate with long stress tests and inference loops.
- Revert by removing those lines and rebooting.

---

## Tests

Unit tests (parser/clamp):

```bash
source .venv/bin/activate
pytest -q
```

---

## Notes on strict output control

Prompt in code enforces:

`Return only the bounding box as [x0,y0,x1,y1] in pixels. No other text.`

Decoder settings for low-latency deterministic output:
- `temperature=0`
- `top_p=1`
- small `max_new_tokens`

Parser is robust to minor output noise and final response is always normalized to 4 integers.
