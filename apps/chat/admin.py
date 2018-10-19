from django.contrib import admin

from .models import ChatMessage, ChatRoom


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('owner', 'assignee', 'creation_time')
    list_filter = ('creation_time', 'owner',)
    search_fields = ('owner', 'assignee')


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'message_time',)
    list_filter = ('message_time',)
    search_fields = ('message_body',)


# register models
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
