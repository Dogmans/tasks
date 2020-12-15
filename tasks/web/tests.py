from django.test import TestCase, Client
from web.models import Queue


class TestApi(TestCase):

	def SetUp(self):
		test_queue = Queue()
		test_queue.save()# TODO - create queue, slots etc.

	def test_get_queues(self):
		client = Client()
		result = client.get("/api/queues")