from django.contrib.auth.models import User
from rest_framework import serializers

from web.models import Queue, Task, Workspace


class UserSerializer(serializers.ModelSerializer):
	# TODO - filter this?
	queues = serializers.PrimaryKeyRelatedField(
		many=True,
		queryset=Queue.objects.all()
	)

	class Meta:
		model = User
		fields = ['id', 'username', 'snippets']


class QueueSerializer(serializers.ModelSerializer):
	class Meta:
		model = Queue
		fields = ["id", "title"]


class TaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = Task
		# TODO - add optional due_by
		fields = ["id", "title", "details"]


class WorkspaceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Workspace
		fields = ["id", "title"]