# Project status

The Python LiveKit agent is implemented in pipeline mode with distinct Deepgram STT,
Groq LLM, and Deepgram TTS stages. It includes ten patient scenarios, call recording,
transcript export, provider preflight checks, and destination safeguards.

The pipeline has passed local validation and a synthetic LiveKit-room test. A real
assessment call has not completed because the configured outbound SIP trunk has no
carrier termination address. The repository deliberately does not claim that the required
ten calls, recordings, bugs, or applicant videos exist. See `SUBMISSION_STATUS.md` for
the current verified evidence and outstanding deliverables.
