from django.urls import path, include
from rest_framework.routers import DefaultRouter
from web import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'queues', views.QueueViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'users', views.UserViewSet)


# The API URLs are now determined automatically by the router.
urlpatterns = [
	path('', include(router.urls)),
]