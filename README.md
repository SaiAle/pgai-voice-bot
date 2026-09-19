# Voice Bot for AI Engineering Challenge

This is an automated voice bot designed to call a test line (+1-805-439-8008) and have conversations with an AI agent to test and evaluate the system.

## Overview

The bot acts as a "patient" testing the medical practice's AI agent system by:
- Making natural conversations to evaluate agent responses
- Testing various scenarios (appointment scheduling, medication refills, etc.)
- Identifying bugs or quality issues in the agent's responses
- Recording and transcribing conversations for analysis

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   py -3.12 -m venv .venv-livekit
   .\.venv-livekit\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   - LiveKit URL, API key, and secret
   - Deepgram API key (for STT and TTS)
   - Groq API key (for LLM generation)
   - Twilio Elastic SIP Trunk credentials for real phone calls (optional for local tests)

## Usage

To run the voice bot:

```bash
.\.venv-livekit\Scripts\python.exe agent.py dev
```

The bot will connect to LiveKit and be ready to receive calls. To make outbound calls to the test number (+1-805-439-8008), you'll need to configure your LiveKit SIP integration or use a compatible telephony provider.

## Architecture

This voice bot uses LiveKit Agents in pipeline mode with separate components:
- **Speech-to-Text**: Deepgram Nova-3 for streaming transcription
- **LLM**: Groq `openai/gpt-oss-20b` for text-only response generation
- **Text-to-Speech**: Deepgram Aura-2 for speech synthesis
- **VAD**: Silero VAD for voice activity detection


The pipeline mode ensures clean separation of concerns and allows for easy swapping of providers. Noise cancellation is enabled to improve audio quality in various environments.

## Local verification

```powershell
.\.venv-livekit\Scripts\python.exe validate.py
```

This performs offline import and pipeline-construction checks. The project also passed a
synthetic LiveKit-room test: a listener received the generated Deepgram audio and the
patient greeting was captured in the transcript.

## Making assessment calls

To test with the actual phone number (+1-805-439-8008), you will need to:
1. Configure a real outbound SIP trunk in LiveKit with a carrier such as Twilio.
2. Use a carrier-issued caller number that you own. Do not use the assessment number as caller ID.
3. Set `LIVEKIT_SIP_TRUNK_ID` to the LiveKit outbound trunk ID.
4. Run `python make_call.py` only after the carrier trunk has answered a test call.

For local testing, you can connect to the room manually and speak with the bot.

## Call Recording and Transcription

The agent requests LiveKit session recording and exports `recording.ogg`, `transcript.txt`, and `session.json` under a timestamped `calls/` folder on shutdown. This export still needs end-to-end verification on a successful assessment call. See `SUBMISSION_STATUS.md` for the verified status.

## Bug Reporting

After each call, review the transcript and audio to identify issues such as:
- Incorrect information provided by the agent
- Failure to follow proper procedures (e.g., checking office hours)
- Poor conversational flow or unnatural responses
- Failure to handle edge cases appropriately

Document findings with timestamps and clear explanations of the expected vs. actual behavior.

## Diagnosing missing audio

Run `run_validation.bat` for offline checks, then `run_agent.bat`.
Development mode registers a worker; audio starts only after a room job is assigned.
Join a new room through a LiveKit frontend/Playground using the same LiveKit project.
This worker has no explicit agent name and uses automatic dispatch.
Look for `Audio session started in room ...` in the terminal.
The worker registration alone does not mean a voice conversation has started.

To test locally through your microphone and speakers, run:

```powershell
.\.venv-livekit\Scripts\python.exe agent.py console
```

Console mode does not create a LiveKit Cloud room. For phone calls, a configured
outbound SIP trunk and a connected SIP participant are also required. The
`LIVEKIT_SIP_TRUNK_ID` setting is used by `make_call.py`.
