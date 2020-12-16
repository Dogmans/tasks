from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets

from web.models import Queue
from web.permissions import IsOwnerOrReadOnly
from web.serializers import QueueSerializer, UserSerializer



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
	queryset = Queue.objects.all()
	serializer_class = QueueSerializer
	permission_classes = [
		permissions.IsAuthenticatedOrReadOnly,
		IsOwnerOrReadOnly
	]

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)
