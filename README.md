## Workflow: Summarizing Meetings into Action Items

This project focuses on automating the process of converting unstructured meeting notes into structured action items.

## Workflow: Summarizing Meetings into Action Items

This project focuses on automating the process of converting unstructured meeting notes into structured action items.

### Input

The system receives unstructured or semi-structured meeting notes. These may include:
- bullet-point notes
- raw transcripts
- informal summaries
- partially incomplete or ambiguous statements

### Output

The system produces a structured summary including:

- Key decisions made during the meeting
- Action items
- Assigned owners (if available)
- Deadlines (if mentioned)
- Open questions or unresolved issues

If certain information (e.g., owner or deadline) is not explicitly stated, the system should indicate it as "Not specified" rather than making assumptions.

### Value

This task is valuable because:

- Meeting notes are often messy and time-consuming to interpret
- Teams need clear and actionable follow-ups to maintain productivity
- Automating this process reduces manual effort and improves consistency
- It helps prevent missed responsibilities and unclear ownership

## Setup

- This project uses the Gemini API through a local environment variable.
- Create a local .env file in the project folder and add:
- GEMINI_API_KEY=your_api_key_here
- Run the app: python app.py

### Files
- `app.py`: the Python prototype
- `prompts.md`: prompt versions and revisions
- `eval_set.md`: evaluation cases
- `report.md`: final report
- `.env.example`: example environment variable file

### Install dependencies
```bash
pip install -r requirements.txt
```
## Environment Setup
Create a local `.env` file and add your API key:

## Video Intro
https://youtu.be/-zg08_garZA
