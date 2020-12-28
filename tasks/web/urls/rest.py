from django.urls import path, include
from rest_framework.routers import DefaultRouter
from web.views import rest as views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'queues', views.QueueViewSet, "queue-detail")
router.register(r'tasks', views.TaskViewSet, "task-detail")
router.register(r'users', views.UserViewSet)
router.register(r'workspaces', views.WorkspaceViewSet, "workspace-detail")


# The API URLs are now determined automatically by the router.
urlpatterns = [
	path('queues/<int:queue_id>/tasks/', views.QueueTaskListView.as_view()),
	path('queues/<int:queue_id>/tasks/<int:pk>/', views.QueueTaskDetailView.as_view()),
	path('workspaces/<int:workspace_id>/queues/', views.WorkspaceQueueListView.as_view()),
	path('workspaces/<int:workspace_id>/queues/<int:pk>/', views.WorkspaceQueueDetailView.as_view()),
	path('', include(router.urls)),
]