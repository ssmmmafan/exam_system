from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Max, Count
from .models import ChatConversation, ChatMessage
from django.contrib.auth.models import User
from exams.models import Exam
from students.models import StudentExamRecord
from .broadcast import broadcast_new_message
import json


def format_last_message(content, max_len=50):
    if not content:
        return ''
    if len(content) <= max_len:
        return content
    return content[:max_len] + '...'


def serialize_message(message, current_user):
    return {
        'id': message.id,
        'content': message.content,
        'type': message.message_type,
        'sender_id': message.sender.id,
        'sender_username': message.sender.username,
        'is_read': message.is_read,
        'is_own': message.sender == current_user,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }


def serialize_message_event(message):
    return {
        'id': message.id,
        'content': message.content,
        'type': message.message_type,
        'sender_id': message.sender.id,
        'sender_username': message.sender.username,
        'is_read': message.is_read,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }


def serialize_conversation_event(conversation):
    last_msg = conversation.messages.order_by('-created_at').first()
    return {
        'id': conversation.id,
        'last_message': format_last_message(last_msg.content if last_msg else ''),
        'last_time': conversation.updated_at.strftime('%Y-%m-%d %H:%M') if conversation.updated_at else '',
    }


def serialize_conversation(conv, user):
    last_msg = conv.messages.order_by('-created_at').first()
    other_users = conv.participants.exclude(id=user.id)
    conv_data = {
        'id': conv.id,
        'type': conv.type,
        'title': conv.title or (conv.exam.title if conv.exam else None),
        'last_message': format_last_message(last_msg.content if last_msg else ''),
        'last_time': conv.updated_at.strftime('%Y-%m-%d %H:%M') if conv.updated_at else '',
        'unread_count': conv.messages.filter(is_read=False).exclude(sender=user).count(),
        'other_users': [{'id': u.id, 'username': u.username} for u in other_users],
    }
    if conv.exam:
        conv_data['exam_title'] = conv.exam.title
        conv_data['exam_id'] = conv.exam.id
    return conv_data


def mark_conversation_read(conversation, user):
    conversation.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)


def find_private_conversation(user_a, user_b):
    for conv in ChatConversation.objects.filter(type='private', participants=user_a).filter(participants=user_b):
        if conv.participants.count() == 2:
            return conv
    return None


def get_or_create_exam_conversation(exam, user):
    conversation = ChatConversation.objects.filter(type='exam', exam=exam).first()
    if not conversation:
        conversation = ChatConversation.objects.create(
            type='exam',
            title=f'{exam.title} - 聊天室',
            exam=exam,
        )
        conversation.participants.add(exam.created_by)

    if not conversation.participants.filter(id=user.id).exists():
        conversation.participants.add(user)

    if user == exam.created_by or user.is_staff:
        student_ids = StudentExamRecord.objects.filter(exam=exam).values_list('student_id', flat=True).distinct()
        for student_id in student_ids:
            conversation.participants.add(student_id)

    return conversation


@login_required
def conversation_list_api(request):
    """获取用户的会话列表"""
    user = request.user
    conversations = ChatConversation.objects.filter(
        participants=user
    ).select_related('exam').prefetch_related('participants').order_by('-updated_at')

    conversations_data = [serialize_conversation(conv, user) for conv in conversations]

    return JsonResponse({
        'success': True,
        'conversations': conversations_data,
    })


@login_required
def conversation_detail_api(request, conversation_id):
    """获取会话详情和消息列表"""
    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            participants=request.user
        )
    except ChatConversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': '会话不存在'}, status=404)

    mark_conversation_read(conversation, request.user)

    messages_data = [
        serialize_message(msg, request.user)
        for msg in conversation.messages.select_related('sender').all()
    ]

    return JsonResponse({
        'success': True,
        'conversation': {
            'id': conversation.id,
            'type': conversation.type,
            'title': conversation.title or (conversation.exam.title if conversation.exam else None),
            'exam_id': conversation.exam_id,
            'exam_title': conversation.exam.title if conversation.exam else None,
        },
        'messages': messages_data,
    })


@login_required
@csrf_exempt
def send_message_api(request, conversation_id):
    """发送消息"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只支持 POST 请求'}, status=400)

    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            participants=request.user
        )
    except ChatConversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': '会话不存在'}, status=404)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        message_type = data.get('type', 'text')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON 解析错误'}, status=400)

    if not content:
        return JsonResponse({'success': False, 'error': '消息内容不能为空'}, status=400)

    message = ChatMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content,
        message_type=message_type,
        is_read=False,
    )

    conversation.updated_at = timezone.now()
    conversation.save(update_fields=['updated_at'])

    serialized = serialize_message(message, request.user)
    broadcast_new_message(
        conversation.id,
        serialize_message_event(message),
        serialize_conversation_event(conversation),
    )

    return JsonResponse({
        'success': True,
        'message': serialized,
    })


@login_required
@csrf_exempt
def create_conversation_api(request):
    """创建新会话"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只支持 POST 请求'}, status=400)

    try:
        data = json.loads(request.body)
        conv_type = data.get('type', 'private')
        title = data.get('title', '').strip()
        exam_id = data.get('exam_id')
        participant_ids = data.get('participants', [])
        target_username = data.get('target_username', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON 解析错误'}, status=400)

    user = request.user

    if conv_type == 'exam' and exam_id:
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': '考试不存在'}, status=404)

        conversation = get_or_create_exam_conversation(exam, user)
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'created': False,
            'conversation': serialize_conversation(conversation, user),
        })

    if conv_type == 'private' and target_username:
        try:
            target_user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': '目标用户不存在'}, status=404)

        if target_user.id == user.id:
            return JsonResponse({'success': False, 'error': '不能与自己私聊'}, status=400)

        existing = find_private_conversation(user, target_user)
        if existing:
            if not existing.participants.filter(id=user.id).exists():
                existing.participants.add(user)
            return JsonResponse({
                'success': True,
                'conversation_id': existing.id,
                'created': False,
                'conversation': serialize_conversation(existing, user),
            })

        conversation = ChatConversation.objects.create(
            type='private',
            title=title or f'{user.username} 与 {target_user.username}',
        )
        conversation.participants.add(user, target_user)
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'created': True,
            'conversation': serialize_conversation(conversation, user),
        })

    conversation = ChatConversation.objects.create(
        type=conv_type,
        title=title or '新的会话',
    )
    conversation.participants.add(user)
    for user_id in participant_ids:
        try:
            participant = User.objects.get(id=user_id)
            conversation.participants.add(participant)
        except User.DoesNotExist:
            continue

    return JsonResponse({
        'success': True,
        'conversation_id': conversation.id,
        'created': True,
        'conversation': serialize_conversation(conversation, user),
    })


@login_required
@csrf_exempt
def ensure_exam_conversation_api(request, exam_id):
    """进入考试聊天室：不存在则创建，并加入当前用户"""
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'success': False, 'error': '只支持 GET/POST 请求'}, status=400)

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return JsonResponse({'success': False, 'error': '考试不存在'}, status=404)

    conversation = get_or_create_exam_conversation(exam, request.user)
    return JsonResponse({
        'success': True,
        'conversation_id': conversation.id,
        'conversation': serialize_conversation(conversation, request.user),
    })
