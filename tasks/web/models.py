from django.db import models
from django.db.models.signals import pre_delete
from web.sort_keys import key_next, key_between


class Workspace(models.Model):
	owner = models.ForeignKey(
		"auth.User",
		related_name="workspaces",
		on_delete=models.CASCADE
	)
	title = models.CharField(max_length=32)


class Queue(models.Model):
	owner = models.ForeignKey(
		"auth.User",
		related_name="queues",
		on_delete=models.CASCADE
	)
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
	title = models.CharField(max_length=20)

	def __str__(self):
		return self.title

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
		query_root = Slot.objects.values_list("sort_key", flat=True)
		sort_key_before = query_root.get(task_id=id_before)
		sort_key_after = query_root.get(task_id=id_after)
		sort_key = key_between(sort_key_before, sort_key_after)
		return self._add_task(task, sort_key)

	def remove_task(self, task):
		'''
		Remove a task from the list, note that this does not delete the task
		:param task:
		'''
		slot = task.slot_set.filter(queue=self).first()
		slot.delete()

	def tasks(self):
		return [slot.task for slot in self.slot_set.order_by("sort_key").select_related("task").all()]


def pre_delete_queue(sender, instance, *args, **kwargs):
	# Remove all tasks associated with this queue only
	for task in instance.tasks():
		if task.slot_set.count() < 2:
			task.delete()

pre_delete.connect(pre_delete_queue, sender=Queue)


class Task(models.Model):
	owner = models.ForeignKey(
		"auth.User",
		related_name="tasks",
		on_delete=models.CASCADE
	)
	title = models.CharField(max_length=32)
	details = models.TextField(null=True)
	created_on = models.DateTimeField(auto_now_add=True)
	due_by = models.DateTimeField(
		null=True,
		blank=True
	)

	def __str__(self):
		return self.title


class Slot(models.Model):
	queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	sort_key = models.CharField(max_length=32)

	

	def __str__(self):
		return "{}-{}".format(self.queue.title, self.task.title)

