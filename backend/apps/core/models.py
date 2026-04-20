from django.db import models
from apps.users.models import User

class SessionMemory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_memories")
    session_id = models.CharField(max_length=128, db_index=True)
    summary = models.TextField(blank=True, verbose_name="摘要")
    messages = models.JSONField(default=list, blank=True, verbose_name="消息列表")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_session_memory"
        verbose_name = "会话记忆"
        verbose_name_plural = "会话记忆"
        unique_together = (("user", "session_id"),)

    def __str__(self):
        return f"{self.user.username} - {self.session_id}"
