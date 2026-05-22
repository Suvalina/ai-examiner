import google.generativeai as genai
import json
import re
import logging
import time

logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self, api_key):

        genai.configure(api_key=api_key)

        # Stable model for current SDK
        self.model = genai.GenerativeModel('models/gemini-pro')

    def evaluate_answer(self, student_answer, model_answer, max_marks, question=None):

        """Evaluate student answer against model answer"""

        question_context = f"\n\nQuestion: {question}" if question else ""

        logger.info("Starting answer evaluation...")

        prompt = f"""
You are an expert AI examiner. Evaluate the student's answer against the model answer.

{question_context}

MODEL ANSWER:
{model_answer}

STUDENT'S ANSWER:
{student_answer}

MAXIMUM MARKS: {max_marks}

Provide a comprehensive evaluation in the following JSON format:

{{
    "marks_awarded": <number between 0 and {max_marks}>,
    "percentage": <percentage score>,
    "strengths": [
        "List specific correct points and concepts the student covered well"
    ],
    "missing_points": [
        "List key concepts or details that were missing or incorrect"
    ],
    "feedback": "Provide detailed constructive feedback",
    "grade": "<A+/A/B+/B/C/D/F based on percentage>"
}}

Return ONLY valid JSON.
"""

        try:

            logger.info("Waiting before API request...")
            time.sleep(8)

            logger.info("Calling Gemini API for evaluation...")

            response = self.model.generate_content(prompt)

            logger.info("Received response from Gemini API")

            result_text = response.text.strip()

            # Extract JSON if wrapped in markdown
            json_match = re.search(
                r'```(?:json)?\s*(\{.*?\})\s*```',
                result_text,
                re.DOTALL
            )

            if json_match:
                result_text = json_match.group(1)

            # Parse JSON
            evaluation = json.loads(result_text)

            # Default values
            evaluation.setdefault('marks_awarded', 0)
            evaluation.setdefault('percentage', 0)
            evaluation.setdefault('strengths', [])
            evaluation.setdefault('missing_points', [])
            evaluation.setdefault('feedback', 'No feedback provided')
            evaluation.setdefault('grade', 'N/A')

            return evaluation

        except json.JSONDecodeError as e:

            logger.error(f"JSON parsing error: {e}")

            return {
                "marks_awarded": 0,
                "percentage": 0,
                "strengths": ["Unable to parse evaluation"],
                "missing_points": ["JSON parsing failed"],
                "feedback": f"Evaluation parsing error: {str(e)}",
                "grade": "N/A"
            }

        except Exception as e:

            error_message = str(e)

            logger.error(f"Gemini API Error: {error_message}")

            # Handle quota exceeded
            if "429" in error_message or "quota" in error_message.lower():

                logger.info("Quota exceeded. Waiting 40 seconds...")

                time.sleep(40)

                try:

                    response = self.model.generate_content(prompt)

                    result_text = response.text.strip()

                    json_match = re.search(
                        r'```(?:json)?\s*(\{.*?\})\s*```',
                        result_text,
                        re.DOTALL
                    )

                    if json_match:
                        result_text = json_match.group(1)

                    evaluation = json.loads(result_text)

                    evaluation.setdefault('marks_awarded', 0)
                    evaluation.setdefault('percentage', 0)
                    evaluation.setdefault('strengths', [])
                    evaluation.setdefault('missing_points', [])
                    evaluation.setdefault('feedback', 'No feedback provided')
                    evaluation.setdefault('grade', 'N/A')

                    return evaluation

                except Exception as retry_error:

                    logger.error(f"Retry failed: {retry_error}")

                    return {
                        "marks_awarded": 0,
                        "percentage": 0,
                        "strengths": [],
                        "missing_points": [],
                        "feedback": f"Retry failed: {str(retry_error)}",
                        "grade": "N/A"
                    }

            return {
                "marks_awarded": 0,
                "percentage": 0,
                "strengths": [],
                "missing_points": [],
                "feedback": f"Error during evaluation: {error_message}",
                "grade": "N/A"
            }