## WebRTC recording FastAPI server example

original repo: https://github.com/aiortc/aiortc/tree/main/examples/server

### Usage

`python3.10 -m venv .venv`
`. .venv/bin/activate`
`pip install -r requirements.txt`
`uvicorn server:app`

Then go to app's address with browser. Click `start` to start the record process and `stop` to finish it. Recorded video must appear in `records` folder.
