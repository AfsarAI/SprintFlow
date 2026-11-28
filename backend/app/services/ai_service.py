import json
import logging
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.ai import SubtaskSuggestionResponse

logger = logging.getLogger(__name__)


def generate_subtask_suggestions(
    task_id: int,
    title: str,
    description: str | None,
    status_str: str,
    priority_str: str,
    due_date_str: str | None,
) -> SubtaskSuggestionResponse:
    """
    Generate structured subtask suggestions using the Gemini API.
    Does NOT save to database. Returns validated Pydantic model.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.strip() == "" or api_key.startswith("your_"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Subtask Generation is unavailable because GEMINI_API_KEY is not configured.",
        )

    prompt = f"""You are an agile software engineering assistant.
Break down the following task into 2 to 5 actionable, practical subtasks.

Task Details:
- Title: {title}
- Description: {description or 'None'}
- Status: {status_str}
- Priority: {priority_str}
- Deadline: {due_date_str or 'None'}

Return ONLY valid JSON matching this structure:
{{
  "task_id": {task_id},
  "task_title": "{title}",
  "subtasks": [
    {{
      "title": "Clear action title",
      "description": "Brief acceptance criteria or details"
    }}
  ]
}}
"""

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SubtaskSuggestionResponse,
                temperature=0.2,
            ),
        )

        response_text = response.text
        if not response_text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI provider returned an empty response.",
            )

        data = json.loads(response_text)
        data["task_id"] = task_id
        data["task_title"] = title
        return SubtaskSuggestionResponse.model_validate(data)

    except HTTPException:
        raise
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse AI JSON response: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned an invalid JSON response.",
        )
    except ValidationError as exc:
        logger.error(f"AI response failed schema validation: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI output failed validation schema: {exc.errors()}",
        )
    except Exception as exc:
        logger.error(f"Unexpected error calling Gemini API: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(exc)}",
        )
