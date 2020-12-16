from django.contrib.auth.models import User
from django.test import TestCase, Client
from web.models import Queue


class TestApi(TestCase):

	def setUp(self):
		super().setUp()
		self._user = User.objects.create(
			username="TestUser",
			email="willfg@gmail.com",
			password="12345",
			first_name="Test",
			last_name="User",
		)
		test_queue = Queue(
			owner = self._user,
			title = "TestQueue"
		)
		test_queue.save()# TODO - create queue, slots etc.

	def test_get_queues(self):
		client = Client()
		result = client.get("/api/queues/")
		self.assertTrue(result.data)