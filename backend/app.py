from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from utils.pdf_processor import PDFProcessor
from utils.gemini_service import GeminiService
from utils.db_connection import db, db_connection
from models.teacher import Teacher
from models.student import Student
from models.evaluation import Evaluation
from bson import ObjectId
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for both development and production
cors_origins = [
    'http://localhost:3000',  # Local development
    'http://localhost:5000',
    os.getenv('FRONTEND_URL', 'http://localhost:3000')  # Production Vercel URL
]
CORS(app, origins=cors_origins)

# Configuration
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

# Initialize services
pdf_processor = PDFProcessor()
gemini_service = GeminiService(Config.GEMINI_API_KEY)

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        doc = doc.copy()
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc
    return doc

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API info"""
    return jsonify({
        'message': 'AI Examiner API',
        'version': '1.0',
        'health_check': '/api/health'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_connection.get_db().command('ping')
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'message': 'AI Examiner API is running',
        'database': db_status
    })

# ==================== TEACHER ROUTES ====================

@app.route('/api/teachers', methods=['POST'])
def create_teacher():
    """Create a new teacher"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        
        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Check if teacher already exists
        existing = Teacher.find_by_email(email)
        if existing:
            return jsonify({'error': 'Teacher with this email already exists'}), 400
        
        teacher = Teacher.create(name, email, subject)
        return jsonify({
            'success': True,
            'teacher': serialize_doc(teacher)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Get teacher by ID"""
    try:
        teacher = Teacher.find_by_id(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        return jsonify({
            'success': True,
            'teacher': serialize_doc(teacher)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers', methods=['GET'])
def get_all_teachers():
    """Get all teachers"""
    try:
        teachers = Teacher.get_all()
        return jsonify({
            'success': True,
            'teachers': serialize_doc(teachers),
            'count': len(teachers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STUDENT ROUTES ====================

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        roll_number = data.get('roll_number')
        class_name = data.get('class')
        
        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Check if student already exists
        existing = Student.find_by_email(email)
        if existing:
            return jsonify({'error': 'Student with this email already exists'}), 400
        
        student = Student.create(name, email, roll_number, class_name)
        return jsonify({
            'success': True,
            'student': serialize_doc(student)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get student by ID"""
    try:
        student = Student.find_by_id(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({
            'success': True,
            'student': serialize_doc(student)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """Get all students"""
    try:
        students = Student.get_all()
        return jsonify({
            'success': True,
            'students': serialize_doc(students),
            'count': len(students)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>/statistics', methods=['GET'])
def get_student_statistics(student_id):
    """Get statistics for a student"""
    try:
        stats = Evaluation.get_student_statistics(student_id)
        if not stats:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_evaluations': 0,
                    'average_marks': 0,
                    'average_percentage': 0
                }
            })
        
        return jsonify({
            'success': True,
            'statistics': serialize_doc(stats)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Delete a teacher"""
    try:
        Teacher.delete(teacher_id)
        return jsonify({'success': True, 'message': 'Teacher deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting teacher: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    try:
        Student.delete(student_id)
        return jsonify({'success': True, 'message': 'Student deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== EVALUATION ROUTES ====================

@app.route('/api/upload-model-answer', methods=['POST'])
def upload_model_answer():
    """Handle model answer upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not Config.allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF allowed.'}), 400
        
        # Save file
        file_path = pdf_processor.save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        # Extract text
        text = pdf_processor.extract_text_from_pdf(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'model_answer': text,
            'message': 'Model answer uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer():
    """Evaluate student answer against model answer and store in database"""
    try:
        # Validate inputs
        if 'student_file' not in request.files:
            return jsonify({'error': 'No student file provided'}), 400
        
        student_file = request.files['student_file']
        model_answer = request.form.get('model_answer')
        max_marks = request.form.get('max_marks')
        question = request.form.get('question', '')
        teacher_id = request.form.get('teacher_id')
        student_id = request.form.get('student_id')
        
        if not model_answer or not max_marks:
            return jsonify({'error': 'Model answer and max marks are required'}), 400
        
        if not Config.allowed_file(student_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Convert max_marks to integer
        try:
            max_marks = int(max_marks)
        except ValueError:
            return jsonify({'error': 'Invalid max marks value'}), 400
        
        # Fetch teacher and student info for storing in evaluation
        teacher_name = 'Unknown'
        student_name = 'Unknown'
        student_rollno = 'N/A'
        
        if teacher_id:
            teacher = Teacher.find_by_id(teacher_id)
            if teacher:
                teacher_name = teacher.get('name', 'Unknown')
        
        if student_id:
            student = Student.find_by_id(student_id)
            if student:
                student_name = student.get('name', 'Unknown')
                student_rollno = student.get('roll_number', 'N/A')
        
        # Save student file
        student_file_path = pdf_processor.save_uploaded_file(
            student_file, 
            app.config['UPLOAD_FOLDER']
        )
        
        # Try text extraction first (instant)
        logger.info("Attempting text extraction...")
        try:
            student_text = pdf_processor.extract_text_from_pdf(student_file_path)
            if len(student_text.strip()) < 100:
                # Not enough text extracted, use Gemini vision
                logger.info("Insufficient text from extraction, using Gemini vision API...")
                images = pdf_processor.convert_pdf_to_images(student_file_path, max_pages=5)
                student_text = pdf_processor.extract_text_from_images_via_gemini(images, gemini_service)
        except Exception as extract_error:
            logger.warning(f"Text extraction failed: {str(extract_error)}, using Gemini vision...")
            images = pdf_processor.convert_pdf_to_images(student_file_path, max_pages=5)
            student_text = pdf_processor.extract_text_from_images_via_gemini(images, gemini_service)
        
        # Evaluate using Gemini
        evaluation_result = gemini_service.evaluate_answer(
            student_text, 
            model_answer, 
            max_marks,
            question
        )
        
        # Store evaluation in database
        evaluation_doc = Evaluation.create(
            teacher_id=teacher_id,
            student_id=student_id,
            question=question,
            model_answer=model_answer,
            student_answer=student_file.filename,
            extracted_text=student_text,
            max_marks=max_marks,
            evaluation_result=evaluation_result,
            teacher_name=teacher_name,
            student_name=student_name,
            student_rollno=student_rollno
        )
        
        # Add extracted text to response
        evaluation_result['extracted_text'] = student_text
        evaluation_result['evaluation_id'] = str(evaluation_doc['_id'])
        
        # Clean up
        os.remove(student_file_path)
        
        return jsonify({
            'success': True,
            'evaluation': evaluation_result
        })
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations', methods=['GET'])
def get_all_evaluations():
    """Get all evaluations"""
    try:
        evaluations = Evaluation.get_all()
        if not evaluations:
            return jsonify([])
        
        return jsonify([serialize_doc(e) for e in evaluations])
    except Exception as e:
        logger.error(f"Error fetching evaluations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    """Get evaluation by ID"""
    try:
        evaluation = Evaluation.find_by_id(evaluation_id)
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
        
        return jsonify({
            'success': True,
            'evaluation': serialize_doc(evaluation)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations/student/<student_id>', methods=['GET'])
def get_student_evaluations(student_id):
    """Get all evaluations for a student"""
    try:
        limit = request.args.get('limit', 10, type=int)
        evaluations = Evaluation.find_by_student(student_id, limit)
        
        return jsonify({
            'success': True,
            'evaluations': serialize_doc(evaluations),
            'count': len(evaluations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations/teacher/<teacher_id>', methods=['GET'])
def get_teacher_evaluations(teacher_id):
    """Get all evaluations by a teacher"""
    try:
        limit = request.args.get('limit', 10, type=int)
        evaluations = Evaluation.find_by_teacher(teacher_id, limit)
        
        return jsonify({
            'success': True,
            'evaluations': serialize_doc(evaluations),
            'count': len(evaluations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations/recent', methods=['GET'])
def get_recent_evaluations():
    """Get recent evaluations"""
    try:
        limit = request.args.get('limit', 20, type=int)
        evaluations = Evaluation.get_recent_evaluations(limit)
        
        return jsonify({
            'success': True,
            'evaluations': serialize_doc(evaluations),
            'count': len(evaluations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluations/<evaluation_id>', methods=['DELETE'])
def delete_evaluation(evaluation_id):
    """Delete an evaluation"""
    try:
        result = Evaluation.delete(evaluation_id)
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Evaluation not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Evaluation deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ocr-only', methods=['POST'])
def ocr_only():
    """Extract text from handwritten PDF without evaluation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not Config.allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save and process file
        file_path = pdf_processor.save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        extracted_text = pdf_processor.extract_text_from_pdf(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Validate required environment variables
    required_vars = ['GEMINI_API_KEY', 'MONGO_URI']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise RuntimeError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    # Create uploads folder if it doesn't exist
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    
    try:
        # Test database connection on startup
        logger.info("Testing database connection...")
        db_connection.connect()
        logger.info("Database connection successful")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        # Close database connection on shutdown
        db_connection.close()
