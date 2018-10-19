from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import AppUser

# Create your models here


class ChatRoom(models.Model):
    """ Chat Room model

    Notes:
        Can handle two users, TS and assignee
    """
    owner = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        related_name='first_user',
        verbose_name=_('Chat owner')
    )
    assignee = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        related_name='second_user',
        verbose_name=_('Assignee')
    )
    link = models.URLField(
        unique=True,
        verbose_name=_('Link')
    )
    creation_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creation time')
    )

    class Meta:
        verbose_name = _('Chat room')
        verbose_name_plural = _('Chat rooms')
        ordering = ('link', )
        indexes = [
            models.Index(
                fields=('link', '-creation_time'),
                name='chat_room_idx'
            )
        ]

    def __str__(self):
        return f'{self.link}'


class ChatMessage(models.Model):
    """ Chat Message model

    Notes:
        Store every message for every room
        This may affect effectiveness
    """
    message_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Message timestamp')
    )
    message_body = models.TextField(
        max_length=2500,
        verbose_name=_('Message text')
    )
    user = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )
    chatroom = models.ForeignKey(
        ChatRoom,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name=_('Chat room')
    )

    class Meta:
        verbose_name = _('Chat message')
        verbose_name_plural = _('Chat messages')
        order_with_respect_to = 'chatroom'
        indexes = [
            models.Index(
                fields=('chatroom', ),
                name='chat_msg_idx'
            )
        ]

    def __str__(self):
        return f'{self.user} on {self.chatroom} - {self.message_body}'
