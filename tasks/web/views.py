from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
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
	# TODO - don't list stuff that people don't have permission for
	queryset = Queue.objects.all()
	serializer_class = QueueSerializer
	permission_classes = [
		permissions.IsAuthenticatedOrReadOnly,
		IsOwnerOrReadOnly
	]

	@action(methods=["POST", "GET", "DELETE"], detail=True)
	def tasks(self, request, *args, **kwargs):
		# TODO - check we have task ownership as well
		# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
		# Handle errors too
		response_status = status.HTTP_200_OK
		queue = self.get_object()
		if request.method == "POST":
			task_id = int(request.data["task_id"])
			task = Task.objects.get(pk=task_id)
			queue.append_task(task)
			response_status = status.HTTP_201_CREATED
		elif request.method == "DELETE":
			task_id = int(request.data["task_id"])
			task = Task.objects.get(pk=task_id)
			queue.remove_task(task)
			response_status = status.HTTP_202_ACCEPTED

		serializer = TaskSerializer(queue.tasks(), many=True)
		return Response(serializer.data, status=response_status)

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
	"""
	This viewset automatically provides `list`, `create`, `retrieve`,
	`update` and `destroy` actions.
	"""
	# https://stackoverflow.com/questions/22760191/django-rest-framework-permissions-for-create-in-viewset
	# TODO - don't list stuff that people don't have permission for
	queryset = Task.objects.all()
	serializer_class = TaskSerializer
	permission_classes = [
		permissions.IsAuthenticatedOrReadOnly,
		IsOwnerOrReadOnly
	]
