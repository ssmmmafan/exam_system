from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def get_chat_group_name(conversation_id):
    return f'chat_{conversation_id}'


def broadcast_new_message(conversation_id, message_data, conversation_data=None):
    """Push a new message to all WebSocket clients in the conversation room."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        get_chat_group_name(conversation_id),
        {
            'type': 'chat.message',
            'message': message_data,
            'conversation': conversation_data,
        },
    )
