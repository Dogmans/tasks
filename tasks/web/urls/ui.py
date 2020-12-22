from django.urls import path, include
from web.views import ui as views


urlpatterns = [
	path('', views.Index.as_view()),
]