from django.contrib.auth.models import User
from django.test import TestCase, Client
from web.models import Queue


def TestBase(TestCase):

	def setUp(self):
		super().setUp()
		self._user = User.objects.create(
			username="TestUser",
			email="willfg@gmail.com",
			password="12345",
			first_name="Test",
			last_name="User",
		)
		self._client = Client()


class TestModels(TestBase):
	'''
	Holds tests that create and update models directly
	Used for preliminary functionality tests before we try to 
	address via the API
	'''

	def test_create_queue(self):
		test_queue = Queue(
			owner = self._user,
			title = "TestQueue"
		)
		self.assertTrue(Queue.objects.all().count())


class TestApi(TestBase):
	'''
	Holds tests that call the REST API to perform functions 
	'''

	def test_create_queue(self):
		# TODO - actually make a Queue via a request
		result = self._client.get("/api/queues/")
		self.assertTrue(result.data)

	def test_create_populate_queue(self):
		'''
		Create a queue with slots and tasks and retrieve via REST
		'''
		pass

	def test_create_insert_queue(self):
		'''
		Create a queue then insert some task in the middle of it and retrieve
		'''
		pass