#!/usr/bin/env python3
import os
import asyncio
from openai import AsyncOpenAI
from livekit import api
from dotenv import load_dotenv
from google.protobuf.duration_pb2 import Duration

load_dotenv()

SCENARIOS = [
    "simple", "switcher", "refill", "weekend", "confused", 
    "interrupter", "insurance", "urgent", "late_night", "cancel"
]

async def make_outbound_call(phone_number: str, scenario_id: str):
    """
    Place an outbound call to a phone number with a specific scenario.
    """
    if phone_number.replace("-", "") != "+18054398008":
        raise ValueError("Only the assessment test number is allowed")
    if scenario_id not in SCENARIOS:
        raise ValueError("Unknown scenario")
    # Fail before dialing when the model account cannot serve a response.
    if os.getenv("GROQ_API_KEY"):
        async with AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        ) as model_client:
            await model_client.chat.completions.create(
                model="openai/gpt-oss-20b", messages=[{"role": "user", "content": "Say OK."}],
                max_tokens=3,
            )
    else:
        async with AsyncOpenAI() as model_client:
            await model_client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": "Say OK."}],
                max_tokens=3,
            )

    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    try:
        trunks = await lkapi.sip.list_sip_outbound_trunk(api.ListSIPOutboundTrunkRequest())
        trunk = next((t for t in trunks.items if t.sip_trunk_id == os.getenv("LIVEKIT_SIP_TRUNK_ID")), None)
        if trunk is None or trunk.address in ("", "0.0.0.0", "localhost", "127.0.0.1"):
            raise ValueError("Configure a real carrier outbound SIP address in LiveKit before dialing")
        if not trunk.numbers or "+18054398008" in trunk.numbers:
            raise ValueError("Configure your own caller number, not the assessment destination")
        print(f"Initiating call for scenario [{scenario_id}] to {phone_number}...")
        
        # We pass the scenario_id as the room_name so the agent.py knows which persona to use
        await lkapi.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_call_to=phone_number.replace("-", ""),
                wait_until_answered=True,
                ringing_timeout=Duration(seconds=30),
                max_call_duration=Duration(seconds=180),
                sip_trunk_id=os.getenv("LIVEKIT_SIP_TRUNK_ID"),
                room_name=scenario_id, 
                participant_identity="patient-bot",
                participant_name=f"Patient {scenario_id}"
            )
        )
        print(f"Phone answered for scenario [{scenario_id}]")
    except Exception as e:
        raise RuntimeError(f"Call failed for {scenario_id}") from e
    finally:
        await lkapi.aclose()

async def run_all_tests():
    TEST_NUMBER = "+1-805-439-8008"
    
    for scenario in SCENARIOS:
        print(f"\n--- Starting Test: {scenario} ---")
        await make_outbound_call(TEST_NUMBER, scenario)
        
        # Wait 3 minutes (180s) for the conversation to complete before starting the next one
        print(f"Waiting 3 minutes for the {scenario} conversation to finish...")
        await asyncio.sleep(180)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
