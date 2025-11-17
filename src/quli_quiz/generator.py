"""Gemini API integration for quiz question generation."""

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from quli_quiz.config import get_gemini_api_key
from quli_quiz.models import Difficulty, Question, QuestionType, Quiz, QuizConfig


class QuizGenerator:
    """Generate quiz questions using Gemini Flash 2.5 with structured output."""

    def __init__(self, api_key: str | None = None):
        """Initialize the generator with API key."""
        if api_key is None:
            api_key = get_gemini_api_key()

        self.api_key = api_key
        # Try model names in order of preference
        self.model_names = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
        ]
        self.model_name = self.model_names[0]

        # Initialize the client
        self.client = genai.Client(api_key=api_key)

    def generate_quiz(self, config: QuizConfig) -> Quiz:
        """Generate a quiz based on the provided configuration."""
        prompt = self._build_prompt(config)
        questions = self._call_gemini(prompt, config)
        return Quiz(topic=config.topic, questions=questions, config=config)

    def _build_prompt(self, config: QuizConfig) -> str:
        """Build the prompt for Gemini."""
        difficulty_text = f" with {config.difficulty.value} difficulty" if config.difficulty else ""
        question_types_text = " and ".join(
            [qt.value.replace("_", " ") for qt in config.question_types]
        )

        prompt = f"""Generate a quiz with {config.num_questions} questions about "{config.topic}".

Requirements:
- Questions should be {question_types_text}{difficulty_text}
- For multiple choice questions, provide exactly 4 options
- For true/false questions, provide options as ["True", "False"]
- Include a brief explanation for each correct answer
- Ensure questions are clear and well-formulated
- Return exactly {config.num_questions} questions"""

        return prompt

    def _call_gemini(self, prompt: str, config: QuizConfig) -> list[Question]:
        """Call Gemini API with structured output using Pydantic schema."""

        # Define the schema for a single question
        class QuestionSchema(BaseModel):
            """Schema for a single question in the response."""

            question_text: str = Field(..., description="The question text")
            question_type: str = Field(..., description="Type: 'multiple_choice' or 'true_false'")
            options: list[str] = Field(..., description="List of answer options")
            correct_answer: str = Field(..., description="The correct answer")
            difficulty: str = Field(..., description="Difficulty: 'easy', 'medium', or 'hard'")
            explanation: str | None = Field(None, description="Explanation of the correct answer")

        # Define the schema for the quiz response
        class QuizResponseSchema(BaseModel):
            """Schema for the complete quiz response."""

            questions: list[QuestionSchema] = Field(
                ..., description=f"List of exactly {config.num_questions} quiz questions"
            )

        # Try each model name until one works
        last_error = None
        for model_name in self.model_names:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=QuizResponseSchema,
                    ),
                )

                # Use the parsed response if available (automatically parsed Pydantic model)
                if hasattr(response, "parsed") and response.parsed is not None:
                    parsed_data = response.parsed
                    # parsed_data is a QuizResponseSchema Pydantic model instance
                    # Access the questions attribute directly
                    if hasattr(parsed_data, "questions"):
                        # Convert Pydantic model instances to dicts
                        questions_list = parsed_data.questions
                        questions_data = []
                        for q in questions_list:
                            if hasattr(q, "model_dump"):
                                # Pydantic v2
                                questions_data.append(q.model_dump())
                            elif hasattr(q, "dict"):
                                # Pydantic v1
                                questions_data.append(q.dict())
                            elif isinstance(q, dict):
                                questions_data.append(q)
                            else:
                                # Try to convert to dict
                                questions_data.append(dict(q))
                    elif isinstance(parsed_data, dict):
                        questions_data = parsed_data.get("questions", [])
                    elif isinstance(parsed_data, list):
                        questions_data = parsed_data
                    else:
                        raise ValueError(f"Unexpected parsed response format: {type(parsed_data)}")
                else:
                    # Fallback: parse JSON from text
                    import json

                    if not hasattr(response, "text") or response.text is None:
                        raise ValueError("Response has no text content and no parsed data")

                    text_data = json.loads(response.text)
                    if isinstance(text_data, dict) and "questions" in text_data:
                        questions_data = text_data["questions"]
                    elif isinstance(text_data, list):
                        questions_data = text_data
                    else:
                        raise ValueError("Unexpected text response format")

                # Convert to Question objects
                questions = self._parse_questions(questions_data, config)

                # Update model name if successful
                self.model_name = model_name

                # If we don't have enough questions, try generating more
                if len(questions) < config.num_questions:
                    remaining = config.num_questions - len(questions)
                    additional_questions = self._generate_additional_questions(
                        config, remaining, model_name
                    )
                    questions.extend(additional_questions[:remaining])

                return questions[: config.num_questions]

            except Exception as e:
                last_error = e
                # Try next model if this one fails
                continue

        # If all models failed, raise the last error
        raise RuntimeError(
            f"Failed to generate quiz from Gemini. Tried models: {', '.join(self.model_names)}. "
            f"Last error: {str(last_error)}"
        ) from last_error

    def _generate_additional_questions(
        self, config: QuizConfig, remaining: int, model_name: str
    ) -> list[Question]:
        """Generate additional questions if we're short."""
        additional_prompt = self._build_prompt(
            QuizConfig(
                topic=config.topic,
                num_questions=remaining,
                difficulty=config.difficulty,
                question_types=config.question_types,
            )
        )
        return self._call_gemini(
            additional_prompt,
            QuizConfig(
                topic=config.topic,
                num_questions=remaining,
                difficulty=config.difficulty,
                question_types=config.question_types,
            ),
        )

    def _parse_questions(
        self, questions_data: list[dict[str, object]], config: QuizConfig
    ) -> list[Question]:
        """Parse question data into Question objects."""
        questions = []
        for item in questions_data:
            try:
                # Ensure options is a list
                options = item.get("options", [])
                if not isinstance(options, list):
                    continue

                question = Question(
                    question_text=str(item["question_text"]),
                    question_type=QuestionType(str(item["question_type"])),
                    options=[str(opt) for opt in options],
                    correct_answer=str(item["correct_answer"]),
                    difficulty=Difficulty(str(item.get("difficulty", "medium"))),
                    explanation=str(item["explanation"]) if item.get("explanation") else None,
                )
                # Validate question
                if not question.validate_options():
                    continue
                questions.append(question)
            except (KeyError, ValueError, TypeError):
                # Skip invalid questions
                continue

        return questions
