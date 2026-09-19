"""Offline checks of the actual agent and installed SDK; makes no calls."""
import inspect
from agent import PatientAgent, SCENARIOS
from livekit.agents import AgentSession
from livekit.plugins import silero, deepgram, groq

for prompt in SCENARIOS.values():
    patient = PatientAgent(prompt)
    assert prompt in patient.instructions
inspect.signature(AgentSession.start).bind(
    None, room=object(), agent=patient
)
silero.VAD.load()
deepgram.STT()
deepgram.TTS()
groq.LLM(model="openai/gpt-oss-20b")
print("PASS: all patient scenarios, session arguments, provider imports, and VAD load")

