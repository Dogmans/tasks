from django.contrib.auth.models import User
from rest_framework import serializers

from web.models import Queue


class UserSerializer(serializers.ModelSerializer):
	queues = serializers.PrimaryKeyRelatedField(many=True, queryset=Queue.objects.all())

	class Meta:
		model = User
		fields = ['id', 'username', 'snippets']


class QueueSerializer(serializers.ModelSerializer):
	class Meta:
		model = Queue
		fields = "__all__"