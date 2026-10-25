from litellm.exceptions import APIConnectionError, AuthenticationError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import TypeVar, cast, List, Annotated
from litellm import acompletion, ModelResponse
from pydantic import BaseModel
from pathlib import Path
from litellm import _turn_on_debug
from string import Template

from src.schemas import *
from src.clerk.deps import currentUser
from src.pdf import get_pdf_text

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
                model=f"openrouter/{model}",
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
        question_prompt_file = Path(
            __file__).parent / "prompts" / "newquestion.txt"
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
        AnswerPromptfile = Path(__file__).parent / \
            "prompts" / "CheckAnswer.txt"
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


@llmRoute.post("/newquestionexample", response_model=QuestionAPIResponse)
async def newquestionexample(
        question_specifications: Annotated[QuestionAPIRequestExamples, Depends(QuestionAPIRequestExamples.as_form)],
        files : List[UploadFile] = File(...),
        current_user: int = Depends(currentUser)
    ) -> QuestionAPIResponse:
    
    extracted_files: list[str] = []
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{file.filename}' is not a PDF.",
            )
        extracted_text = await get_pdf_text(file)
        extracted_files.append(
            f"--- File: {file.filename} ---\n{extracted_text}"
        )
    combined_text = "\n\n".join(extracted_files)
    
    question_prompt_file = Path(
        __file__).parent / "prompts" / "newquestion.txt"
    template_text = question_prompt_file.read_text(encoding="utf-8")
    prompt_template = Template(template_text)
    
    userspecifications = question_specifications.UserPrompt.strip()
    if len(userspecifications) < 3:
        userspecifications = "From the provided examples, randomly select exactly one example that matches the requested language and difficulty. Use only that selected example as a style and scope reference. Generate one original question with the same general type and complexity. Do not copy, quote, reveal, or closely paraphrase the selected example. Do not use or combine any other examples."
    
    prompt = prompt_template.substitute(
        difficulty=question_specifications.diff,
        language=question_specifications.language,
        user_specifications=userspecifications,
        examples=combined_text
    )
    
    return await callLLM(
                prompt=prompt,
                model=question_specifications.model,
                schema=QuestionAPIResponse,)

