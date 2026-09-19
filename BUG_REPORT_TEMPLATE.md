# Bug Report Template

## Bug Report Format

For each issue you find during testing, please document:

**Bug:** [Clear, concise description of the issue]
**Severity:** [Low/Medium/High/Critical]
**Call:** [transcript-X.txt at timestamp]
**Details:** [Detailed explanation of what happened, what should have happened, and why it's a problem]
**Expected:** [What the agent should have done or said]
**Actual:** [What the agent actually did or said]

## Example Bug Report Entry

Bug: Agent confirms appointment for Sunday, but the practice is closed on weekends
Severity: High
Call: transcript-07.txt at 1:23
Details: When asked "Can I come in Sunday at 10am?", the agent responded, "I've scheduled you for Sunday at 10 am" without checking office hours. Should have informed the patient the office is closed on weekends and offered the next available weekdays.
Expected: Agent should check office hours before confirming appointments and inform patients of scheduling limitations
Actual: Agent confirmed the Sunday appointment without checking availability

## How to Use This Template

1. After each test call, review the transcript and audio recording
2. Identify any instances where the agent's response was incorrect, incomplete, or inappropriate
3. Fill out the template above for each bug found
4. Be specific about timestamps and quote relevant portions of the conversation
5. Focus on meaningful issues that impact patient care or experience, not minor nitpicks

## Categories of Issues to Look For

- **Medical Accuracy**: Incorrect medical information or advice
- **Procedural Errors**: Failure to follow standard medical office procedures
- **Communication Issues**: Unclear, confusing, or inappropriate responses
- **Edge Case Handling**: Poor performance with unusual or complex requests
- **Appointment Scheduling**: Errors in booking, rescheduling, or canceling appointments
- **Information Provision**: Giving wrong information about hours, locations, insurance, etc.
- **Empathy and Tone**: Responses that lack appropriate empathy or bedside manner
