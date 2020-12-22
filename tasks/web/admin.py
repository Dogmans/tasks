from django.contrib import admin
from web.models import Queue, Task, Slot


class QueueAdmin(admin.ModelAdmin):
	list_display = ["title", "owner"]


class TaskAdmin(admin.ModelAdmin):
	list_display = ["title", "due_by", "owner"]


class SlotAdmin(admin.ModelAdmin):
	queue_title = "queue__title"
	task_title = "task__title"
	list_display = ["queue_title", "task_title", "sort_key"]


admin.site.register(Queue, QueueAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Slot, SlotAdmin)