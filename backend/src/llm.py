from litellm.exceptions import APIConnectionError, AuthenticationError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, status
from typing import TypeVar, cast
from typing import cast
from litellm import acompletion, ModelResponse
from pydantic import BaseModel
from pathlib import Path

from src.schemas import QuestionAPIResponse, QuestionAPIRequest, AnswerAPIResponse, AnswerAPIRequest
from src.auth import verifyToken

llmRoute = APIRouter()

T = TypeVar("T", bound=BaseModel)

async def callLLM(prompt: str, model: str, schema: type[T]) -> T:
    response = cast(ModelResponse, await acompletion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format=schema,
        stream=False,
    ))

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("LLM returned no content")

    return schema.model_validate_json(content)

@llmRoute.post("/newquestion", response_model=QuestionAPIResponse)
async def newquestion(
    question_specifications: QuestionAPIRequest,
    current_user: int = Depends(verifyToken),
) -> QuestionAPIResponse:
    try:
        QuestionPromptfile = Path(__file__).parent / "prompts" / "newquestion.txt"
        prompt = QuestionPromptfile.read_text(encoding="utf-8")

        prompt += f"""
                    specifications:
                    \tdifficulty: {question_specifications.diff}
                    \tuser specifications: {question_specifications.UserPrompt}
                    \tlanguage: {question_specifications.language}
                    """

        return await callLLM(
            prompt,
            question_specifications.model,
            QuestionAPIResponse,
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
    Answer: AnswerAPIRequest,
    current_user: int = Depends(verifyToken)
):
    try:
            AnswerPromptfile = Path(__file__).parent / "prompts" / "CheckAnswer.txt"
            prompt = AnswerPromptfile.read_text(encoding="utf-8")
    
            prompt += f"""
                        question: \n{Answer.Question}
                        User's Answer: \n{Answer.Answer}
                        """
    
            return await callLLM(
                prompt,
                Answer.model,
                AnswerAPIResponse
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
                    detail="Failed to check answer",
                )