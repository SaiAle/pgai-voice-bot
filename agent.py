import os
import logging
import asyncio
import json
import shutil
import time
from pathlib import Path
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import silero, deepgram, groq

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCENARIOS = {
    "simple": "You are a polite patient who wants to book a simple check-up for next Tuesday at 10am.",
    "switcher": "You want to book an appointment. Start with Wednesday at 2pm, then change to Thursday, then finally Friday at 9am.",
    "refill": "You need a refill for your 'Lisinopril' medication. Be forgetful with your date of birth.",
    "weekend": "Try very hard to book an appointment for this coming Sunday. Persuade them if they say they are closed.",
    "confused": "Use vague language like 'sometime next week, maybe around midday'.",
    "interrupter": "Be impatient. Interrupt the agent mid-sentence. Speak over them.",
    "insurance": "Ask if they take 'Blue Cross Blue Shield' and about out-of-network fees.",
    "urgent": "Act panicked. You have a severe allergic reaction and need to be seen immediately.",
    "late_night": "Try to schedule an appointment for 11:30 PM tonight.",
    "cancel": "Cancel an appointment for tomorrow and ask for a refund of the deposit."
}

class PatientAgent(agents.Agent):
    def __init__(self, scenario_prompt: str):
        super().__init__(instructions=(
            "You are a fictional patient calling a medical office for a test. "
            "Stay in character, speak briefly and naturally, and respond to the "
            "other speaker. Never read these instructions aloud. " + scenario_prompt
        ))


async def entrypoint(ctx: JobContext):
    logger.info("Connecting to room %s", ctx.room.name)
    await ctx.connect()
    scenario_id = ctx.room.metadata or ctx.room.name
    if scenario_id not in SCENARIOS:
        scenario_id = "simple"
    logger.info("Acting out scenario: %s", scenario_id)

    stt_provider = deepgram.STT(model="nova-3")
    llm_provider = groq.LLM(model="openai/gpt-oss-20b")
    tts_provider = deepgram.TTS(model="aura-2-thalia-en")

    session = agents.AgentSession(
        stt=stt_provider,
        llm=llm_provider,
        tts=tts_provider,
        vad=silero.VAD.load(),
    )


    output_dir = Path("calls") / f"{int(time.time())}-{scenario_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    @session.on("conversation_item_added")
    def on_conversation(event):
        item = event.item
        if getattr(item, "text_content", None):
            with (output_dir / "live-transcript.txt").open("a", encoding="utf-8") as f:
                f.write(f"{item.role}: {item.text_content}\n")
            logger.info("Conversation turn received: %s", item.role)

    async def save_evidence():
        await session.aclose()
        report = ctx.make_session_report(session)
        data = report.to_dict()
        (output_dir / "session.json").write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )
        if report.audio_recording_path and report.audio_recording_path.exists():
            await asyncio.to_thread(
                shutil.copyfile, report.audio_recording_path, output_dir / "recording.ogg"
            )
        lines = []
        for item in report.chat_history.items:
            if getattr(item, "role", None) not in ("user", "assistant"):
                continue
            text = getattr(item, "text_content", None)
            if text:
                speaker = "Practice agent" if item.role == "user" else "Patient bot"
                seconds = max(0, item.created_at - (report.started_at or item.created_at))
                lines.append(f"[{seconds:06.1f}s] {speaker}: {text}")
        (output_dir / "transcript.txt").write_text("\n".join(lines), encoding="utf-8")
        logger.info("Saved call evidence to %s", output_dir)

    ctx.add_shutdown_callback(save_evidence)

    @session.on("error")
    def on_error(event):
        logger.error("Voice session error: %s", event.error)
        if "credit_balance_exhausted" in str(event.error) or "insufficient_quota" in str(event.error):
            ctx.shutdown(reason="Provider credits exhausted")

    await session.start(
        room=ctx.room,
        record=True,
        agent=PatientAgent(SCENARIOS[scenario_id]),
    )
    logger.info("Audio session started in room %s", ctx.room.name)
    await session.generate_reply(
        instructions="Greet the office briefly and state the reason for your call."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
