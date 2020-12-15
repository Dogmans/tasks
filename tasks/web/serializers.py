from django.contrib.auth.models import User
from rest_framework import serializers

from web.models import TaskQueue


class UserSerializer(serializers.ModelSerializer):
	queues = serializers.PrimaryKeyRelatedField(many=True, queryset=Queue.objects.all())

	class Meta:
		model = User
		fields = ['id', 'username', 'snippets']


class TaskQueueSerializer(serializers.ModelSerializer):
	class Meta:
		model = TaskQueue
		fields = "__all__"