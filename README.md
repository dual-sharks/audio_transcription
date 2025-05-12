# audio_transcription

## Architecture
The application uses a microservices architecture with three main components:
- FastAPI service: Handles HTTP requests and manages transcription jobs
- Whisper service: Processes audio files using OpenAI's Whisper model
- Redis: Message broker for async communication between services

## Setup Instructions

### Poetry Setup (Development)
1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install project dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### VS Code Configuration
1. Open the project in VS Code
2. Open a Jupyter notebook
3. Click on the kernel selector in the top right corner
4. Select "Select Another Kernel..."
5. Choose the Poetry environment (it should be listed as `Python 3.x.x ('audio_transcription-...')`)

### Finding the Poetry Environment Path
If you need to manually locate the Poetry environment path:
1. Run `poetry env info` in your terminal
2. Look for the "Path" field in the output
3. Use this path when selecting the kernel in VS Code if it's not automatically detected

Note: The Poetry environment path is typically located in `~/.cache/pypoetry/virtualenvs/` on Unix systems.

### Running with Docker Compose
1. Build and start all services:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

### Testing the Transcription API
A sample audio file (JFK's "We choose to go to the moon" speech) is included in the repository for testing purposes. You can test the transcription API using:

1. Submit a transcription request:
   ```bash
   curl -X POST http://localhost:8000/transcribe/jfk.flac
   ```
   This will return a request ID.

2. Check the transcription status:
   ```bash
   curl http://localhost:8000/transcription/{request_id}
   ```
   Replace `{request_id}` with the ID received from the previous request.

The API will return a JSON response containing:
- `text`: The full transcribed text
- `segments`: Detailed segments of the transcription with timestamps

Note: The first request might take longer as it needs to download the Whisper model.