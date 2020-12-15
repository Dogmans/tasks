from django.db import models


class Queue(models.Model):
	owner = models.ForeignKey(
		"auth.User",
		related_name="queues",
		on_delete=models.CASCADE
	)
	title = models.CharField(max_length=20)


class Task(models.Model):
	created_on = models.DateTimeField(auto_now_add=True)
	due_by = models.DateTimeField()


class Slot(models.Model):
	queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	sort_key = models.CharField(max_length=32)

