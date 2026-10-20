from litellm.exceptions import APIConnectionError, AuthenticationError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, status
from typing import TypeVar, cast
from typing import cast
from litellm import acompletion, ModelResponse
from pydantic import BaseModel
from pathlib import Path
from litellm import _turn_on_debug
from string import Template

from src.schemas import (
    QuestionAPIResponse,
    QuestionAPIRequest,
    AnswerAPIResponse,
    AnswerAPIRequest,
)
from src.deps import currentUser

llmRoute = APIRouter()

T = TypeVar("T", bound=BaseModel)
JSON_SYSTEM_PROMPT = """
You are a JSON-only API.
You must return exactly one valid JSON object and nothing else.
Rules:
- Do not output markdown.
- Do not output any preamble or postamble
- Do not use code fences.
- Do not output XML tags such as <question>.
- Do not include an introduction, explanation, solution, hint, schema, example, or extra keys.
- Do not write any text before or after the JSON object.
Any output that is not valid JSON is invalid.
""".strip()

# async def callLLM(prompt: str, model: str, schema: type[T]) -> T:
#     _turn_on_debug()
#     response = cast(ModelResponse, await acompletion(
#         model=f"{model}",
#         api_key="",
#         messages=[
#                 {
#                     "role": "system",
#                     "content": JSON_SYSTEM_PROMPT,
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 },
#             ],
#         stream=False,
#     ))

#     content = response.choices[0].message.content
#     print(content)
#     if content is None:
#         raise ValueError("LLM returned no content")

#     print(content)

#     return schema.model_validate_json(content)


async def callLLM(prompt: str, model: str, schema: type[T]) -> T:
    try:
        response = cast(
            ModelResponse,
            await acompletion(
                model="openrouter/minimax/minimax-m3.1-flash:free",
                api_key="",
                messages=[
                    {
                        "role": "system",
                        "content": JSON_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
                stream=False,
            ),
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned no content")
        return schema.model_validate_json(content)
    except Exception as exc:
        print(f"LLM ERROR TYPE: {type(exc).__name__}")
        print(f"LLM ERROR: {exc!r}")
        raise


@llmRoute.post("/newquestion", response_model=QuestionAPIResponse)
async def newquestion(
    question_specifications: QuestionAPIRequest,
    current_user: int = Depends(currentUser),
) -> QuestionAPIResponse:
    try:
        question_prompt_file = Path(__file__).parent / "prompts" / "newquestion.txt"
        template_text = question_prompt_file.read_text(encoding="utf-8")
        prompt_template = Template(template_text)
        prompt = prompt_template.substitute(
            difficulty=question_specifications.diff,
            language=question_specifications.language,
            user_specifications=question_specifications.UserPrompt.strip(),
        )
        return await callLLM(
            prompt=prompt,
            model=question_specifications.model,
            schema=QuestionAPIResponse,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question prompt template is missing",
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider authentication failed",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to the LLM provider",
        )
    except BadRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid LLM request: {exc.message}",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned an invalid response format",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate a question",
        )


@llmRoute.post("/checkAnswer", response_model=AnswerAPIResponse)
async def CheckAnswer(
    Answer: AnswerAPIRequest, current_user: int = Depends(currentUser)
):
    try:
        AnswerPromptfile = Path(__file__).parent / "prompts" / "CheckAnswer.txt"
        prompt = AnswerPromptfile.read_text(encoding="utf-8")

        prompt += f"""
                        question: \n{Answer.Question}
                        User's Answer: \n{Answer.Answer}
                        """

        return await callLLM(prompt, Answer.model, AnswerAPIResponse)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question prompt template is missing",
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider authentication failed",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to the LLM provider",
        )
    except BadRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid LLM request: {exc.message}",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned an invalid response format",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check answer",
        )
