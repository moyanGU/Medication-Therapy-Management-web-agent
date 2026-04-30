from django.contrib import admin
from .models import SessionMemory, AgentPermission

@admin.register(SessionMemory)
class SessionMemoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'updated_at')
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AgentPermission)
class AgentPermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'action_type', 'state', 'updated_at')
    list_filter = ('role', 'state', 'action_type')
    search_fields = ('role', 'action_type')
    readonly_fields = ('created_at', 'updated_at')
