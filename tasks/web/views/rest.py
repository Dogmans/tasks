from django.contrib.auth.models import User
from django.views.generic import TemplateView

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets

from web.models import Queue, Task
from web.permissions import IsOwnerOrReadOnly
from web.serializers import QueueSerializer, TaskSerializer, UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	This viewset automatically provides `list` and `retrieve` actions.
	"""
	queryset = User.objects.all()
	serializer_class = UserSerializer


class QueueViewSet(viewsets.ModelViewSet):
	"""
	This viewset automatically provides `list`, `create`, `retrieve`,
	`update` and `destroy` actions.
	"""
	# https://stackoverflow.com/questions/22760191/django-rest-framework-permissions-for-create-in-viewset
	serializer_class = QueueSerializer
	# TODO - this is too lax, change this for updating etc.
	permission_classes = [
		permissions.IsAuthenticated,
		IsOwnerOrReadOnly
	]
	
	def get_queryset(self):
		return Queue.objects.filter(owner=self.request.user)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class QueueTaskView():
	serializer_class = TaskSerializer

	def get_queue(self):
		return Queue.objects.get(owner=self.request.user, id=self.kwargs.get("queue_id"))

	def get_queryset(self):
		return Task.objects.filter(slot__queue=(
			self.get_queue()
		))


class QueueTaskListView(QueueTaskView, generics.ListCreateAPIView):

	def create(self, request, *args, **kwargs):
		# Pass existing object into serializer if we are passing exsting id
		task_id = request.data.get("task_id")
		if task_id:
			task = Task.objects.get(owner=self.request.user, pk=task_id)
			serializer = self.get_serializer(task, many=False)
		else:
			serializer = self.get_serializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			task = serializer.save(owner=self.request.user)

		self.append_task(task)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def append_task(self, task):
		queue = self.get_queue()
		queue.append_task(task)


class QueueTaskDetailView(QueueTaskView, generics.DestroyAPIView):

	def perform_destroy(self, instance):
		queue = self.get_queue()
		queue.remove_task(instance)


class TaskViewSet(viewsets.ModelViewSet):
	"""
	This viewset automatically provides `list`, `create`, `retrieve`,
	`update` and `destroy` actions.
	"""
	# https://stackoverflow.com/questions/22760191/django-rest-framework-permissions-for-create-in-viewset
	serializer_class = TaskSerializer
	permission_classes = [
		permissions.IsAuthenticated,
		IsOwnerOrReadOnly
	]

	def get_queryset(self):
		return Task.objects.filter(owner=self.request.user)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)
