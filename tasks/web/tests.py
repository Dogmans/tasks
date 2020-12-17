from django.contrib.auth.models import User
from django.test import TestCase, Client
from web.models import Queue, Task


class TestBase(TestCase):

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
		queue = Queue(
			owner = self._user,
			title = "TestQueue"
		)
		queue.save()
		self.assertTrue(Queue.objects.all().count())

	def test_push_tasks(self):
		queue = Queue(
			owner = self._user,
			title = "TestQueue"
		)
		queue.save()

		for title in ["TestTask1", "TestTask2"]:
			task = Task(
				title=title,
				details="Something"
			)
			task.save()
			queue.append_task(task)

		tasks = queue.tasks()
		self.assertEqual(tasks[-1].title, "TestTask2")


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