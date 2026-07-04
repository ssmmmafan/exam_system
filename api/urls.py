from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'Exam System API',
        'version': '1.0',
        'endpoints': {
            'student': {
                'dashboard': '/api/student/dashboard/',
                'exams': '/api/student/exams/',
                'exam_detail': '/api/student/exam/{exam_id}/',
                'exam_taking': '/api/student/exam/{exam_id}/take/',
                'save_answer': '/api/student/exam/{exam_id}/save/',
                'submit_exam': '/api/student/exam/{exam_id}/submit/',
                'results': '/api/student/results/',
                'exam_result': '/api/student/result/{record_id}/',
                'wrong_questions': '/api/student/wrong-questions/',
                'profile': '/api/student/profile/',
            },
            'teacher': {
                'dashboard': '/api/teacher/dashboard/',
                'questions': '/api/teacher/questions/',
                'question_detail': '/api/teacher/questions/{question_id}/',
                'import_questions': '/api/teacher/questions/import/',
                'exams': '/api/teacher/exams/',
                'exam_detail': '/api/teacher/exams/{exam_id}/',
                'grade': '/api/teacher/grade/{record_id}/',
            },
            'chat': {
                'conversations': '/api/chat/conversations/',
                'create_conversation': '/api/chat/conversations/create/',
                'conversation_detail': '/api/chat/conversations/{conversation_id}/',
                'send_message': '/api/chat/conversations/{conversation_id}/send/',
            },
        },
    })

urlpatterns = [
    path('', api_root),
    path('login/', include('users.api_urls')),
    path('student/', include('students.api_urls')),
    path('teacher/', include('teachers.api_urls')),
    path('chat/', include('chat.api_urls')),
]
