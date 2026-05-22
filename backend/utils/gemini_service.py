import google.generativeai as genai
import json
import re
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash: newer model with better quotas
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
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
        "List specific correct points and concepts the student covered well",
        "Include at least 3-5 points if applicable"
    ],
    "missing_points": [
        "List key concepts or details that were missing or incorrect",
        "Include at least 2-3 points if applicable"
    ],
    "feedback": "Provide detailed constructive feedback (2-3 sentences) explaining the evaluation, what was done well, and areas for improvement",
    "grade": "<A+/A/B+/B/C/D/F based on percentage>"
}}

Be fair, constructive, and specific in your evaluation. Consider:
- Conceptual understanding
- Accuracy of information
- Completeness of the answer
- Clarity and structure

Return ONLY valid JSON, no additional text.
"""
        
        try:
            logger.info("Calling Gemini API for evaluation...")
            response = self.model.generate_content(prompt)
            logger.info("Received response from Gemini API")
            result_text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            
            # Parse JSON
            evaluation = json.loads(result_text)
            
            # Validate and set defaults
            evaluation.setdefault('marks_awarded', 0)
            evaluation.setdefault('percentage', 0)
            evaluation.setdefault('strengths', [])
            evaluation.setdefault('missing_points', [])
            evaluation.setdefault('feedback', 'No feedback provided')
            evaluation.setdefault('grade', 'N/A')
            
            return evaluation
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "marks_awarded": 0,
                "percentage": 0,
                "strengths": ["Unable to parse evaluation results"],
                "missing_points": ["Error in evaluation process"],
                "feedback": f"Evaluation error: {str(e)}. Raw response: {result_text[:200]}",
                "grade": "N/A"
            }
        except Exception as e:
            return {
                "marks_awarded": 0,
                "percentage": 0,
                "strengths": [],
                "missing_points": [],
                "feedback": f"Error during evaluation: {str(e)}",
                "grade": "N/A"
            }
