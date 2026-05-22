import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes - Gemini vision is much faster than EasyOCR
});

// Teacher APIs
export const createTeacher = async (name, email, subject) => {
  const response = await api.post('/api/teachers', { name, email, subject }, {
    headers: { 'Content-Type': 'application/json' }
  });
  return response.data;
};

export const getTeacher = async (teacherId) => {
  const response = await api.get(`/api/teachers/${teacherId}`);
  return response.data;
};

export const getAllTeachers = async () => {
  const response = await api.get('/api/teachers');
  return response.data;
};

export const deleteTeacher = async (teacherId) => {
  const response = await api.delete(`/api/teachers/${teacherId}`);
  return response.data;
};

// Student APIs
export const createStudent = async (name, email, rollNumber, className) => {
  const response = await api.post('/api/students', { 
    name, 
    email, 
    roll_number: rollNumber, 
    class: className 
  }, {
    headers: { 'Content-Type': 'application/json' }
  });
  return response.data;
};

export const getStudent = async (studentId) => {
  const response = await api.get(`/api/students/${studentId}`);
  return response.data;
};

export const getAllStudents = async () => {
  const response = await api.get('/api/students');
  return response.data;
};

export const deleteStudent = async (studentId) => {
  const response = await api.delete(`/api/students/${studentId}`);
  return response.data;
};

export const getStudentStatistics = async (studentId) => {
  const response = await api.get(`/api/students/${studentId}/statistics`);
  return response.data;
};

// Evaluation APIs
export const uploadModelAnswer = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/upload-model-answer', formData);
  return response.data;
};

export const evaluateAnswer = async (formDataOrFile, modelAnswer, maxMarks, question = '', teacherId = null, studentId = null) => {
  // Handle both FormData object and individual parameters
  let formData;
  
  if (formDataOrFile instanceof FormData) {
    // If FormData is passed directly, use it as-is
    formData = formDataOrFile;
  } else {
    // Otherwise create FormData from individual parameters
    formData = new FormData();
    formData.append('student_file', formDataOrFile);
    formData.append('model_answer', modelAnswer);
    formData.append('max_marks', maxMarks);
    if (question) formData.append('question', question);
    if (teacherId) formData.append('teacher_id', teacherId);
    if (studentId) formData.append('student_id', studentId);
  }
  
  const response = await api.post('/api/evaluate-answer', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getEvaluation = async (evaluationId) => {
  const response = await api.get(`/api/evaluations/${evaluationId}`);
  return response.data;
};

export const getEvaluations = async () => {
  const response = await api.get('/api/evaluations');
  return response.data;
};

export const getStudentEvaluations = async (studentId, limit = 10) => {
  const response = await api.get(`/api/evaluations/student/${studentId}?limit=${limit}`);
  return response.data;
};

export const getTeacherEvaluations = async (teacherId, limit = 10) => {
  const response = await api.get(`/api/evaluations/teacher/${teacherId}?limit=${limit}`);
  return response.data;
};

export const getRecentEvaluations = async (limit = 20) => {
  const response = await api.get(`/api/evaluations/recent?limit=${limit}`);
  return response.data;
};

export const deleteEvaluation = async (evaluationId) => {
  const response = await api.delete(`/api/evaluations/${evaluationId}`);
  return response.data;
};

export const extractTextOnly = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/ocr-only', formData);
  return response.data;
};

export default api;
