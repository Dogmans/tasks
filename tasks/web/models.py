from django.db import models
from web.sort_keys import key_next, key_between


class Queue(models.Model):
	owner = models.ForeignKey(
		"auth.User",
		related_name="queues",
		on_delete=models.CASCADE
	)
	title = models.CharField(max_length=20)

	def _add_task(self, task, sort_key):
		slot = Slot(
			queue=self,
			task=task,
			sort_key=sort_key
		)
		slot.save()
		return sort_key

	def append_task(self, task):
		'''
		Add a task to the "end" of the queue
		:param task: Task
		'''
		slot_last = self.slot_set.order_by("-sort_key").first()
		sort_key = key_next(slot_last and slot_last.sort_key)
		return self._add_task(task, sort_key)

	def insert_task(self, task, id_before, id_after):
		'''
		Insert a task between two existing slots / tasks in the queue
		:param task: Task
		:param id_before: int
		:param id_after: int
		'''
		sort_key_before = Slot.objects.get(task_id=id_before).sort_key
		sort_key_after = Slot.objects.get(task_id=id_after).sort_key
		sort_key = key_between(sort_key_before, sort_key_after)
		return self._add_task(task, sort_key)

	def tasks(self):
		return [slot.task for slot in self.slot_set.order_by("sort_key").select_related("task").all()]


class Task(models.Model):
	title = models.CharField(max_length=32)
	details = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	due_by = models.DateTimeField(
		null=True,
		blank=True
	)


class Slot(models.Model):
	queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	sort_key = models.CharField(max_length=32)

