# InsuranceAI Voice Bot (Docker Edition)

This project runs a full-stack AI voice assistant inside a Docker container. The container bundles the Python environment, C/C++ build tools required by some native packages, `ffmpeg` (for audio), and a CPU-only runtime for model inference.

> Note: This Docker image is intended to simplify setup on machines without native builds. For best performance with large models you may still prefer a host GPU setup outside the container.

## Requirements

- Docker Desktop (make sure it's installed and running)

## How to run (Easy Mode)

1. Build the Docker image

	Open a terminal in the project's root directory and run (this may take several minutes while dependencies and model files are prepared):

	```powershell
	docker build -t insurance-bot .
	```

2. Run the container

	After a successful build, start the container. This will launch the backend server inside the container:

	```powershell
	docker run -p 8765:8765 insurance-bot
	```

	The `-p 8765:8765` flag maps port `8765` on your host to port `8765` inside the container. You should see the Python server startup logs in the terminal.

	Optional: mount a local `models/` directory so the container uses your host models (recommended to avoid re-downloading):

	```powershell
	docker run -p 8765:8765 -v ${PWD}/models:/app/models insurance-bot
	```

3. Open the frontend

	- You can open the `index.html` file in `backend/water` directly in your browser. The page connects to the WebSocket server at `ws://localhost:8765` and should show a "Connected" status.
	- Alternatively, serve the frontend directory with a simple HTTP server and open the served URL in a browser (recommended to avoid browser file-origin restrictions):

	```powershell
	cd backend/water
	python -m http.server 8000
	# then open http://localhost:8000 in your browser
	```

## Ports

- `8765` — WebSocket backend (audio transcription / chat)
- `8000` — optional static server for the frontend if you use `python -m http.server`

## Troubleshooting

- If the server fails to start due to missing model files, ensure you have a compatible GGUF or HF model in the mounted `models/` directory or included at image build time.
- For OCR and PDF extraction to work correctly, Tesseract and Poppler are required. The container includes these in most builds, but if you run the code on the host you may need to install them separately.
- If you want improved audio performance or GPU acceleration, run the model on a host with the appropriate GPU drivers and a GPU-enabled runtime (this image is CPU-only by default).

## Advanced Notes

- To persist logs or configuration, mount host directories into the container with `-v`.
- If you customize ports or environment variables, update the frontend connection URL (`ws://`) accordingly.

## You're ready

Once the container is running and the frontend is loaded, you should be able to speak or type queries and receive responses from the assistant.

If you'd like, I can also:
- add a small `docker-compose.yml` that mounts `models/` and exposes ports, or
- update the README with recommended model mount paths and example `docker run` commands for Windows PowerShell.

