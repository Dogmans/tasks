from django.contrib.auth.models import User
from django.test import TestCase, Client
from web.models import Queue, Slot, Task


class TestBase(TestCase):

	def setUp(self):
		super().setUp()
		self._user = User.objects.create_user(
			username="TestUser",
			email="willfg@gmail.com",
			password="12345",
			first_name="Test",
			last_name="User",
		)
		self._user.save()

		self._client = Client()
		self._client.login(
			username="TestUser",
			password="12345"
		)

		self._queue = Queue(
			owner = self._user,
			title = "TestQueue"
		)
		self._queue.save()

		for title in ["TestTask1", "TestTask2", "TestTask3"]:
			task = Task(
				title=title,
				details="Something"
			)
			task.save()
			self._queue.append_task(task)


class TestModels(TestBase):
	'''
	Holds tests that create and update models directly
	Used for preliminary functionality tests before we try to 
	address via the API
	'''

	def test_create_queue(self):
		self.assertTrue(Queue.objects.all().count())

	def test_push_delete_tasks(self):
		# Check end of queue
		tasks = self._queue.tasks()
		self.assertEqual(tasks[-1].title, "TestTask3")

		# Check beginning of queue after removal of first item
		tasks[0].delete()
		tasks = self._queue.tasks()
		self.assertEqual(tasks[0].title, "TestTask2")

	def test_push_insert_task(self):
		# Insert a task between 1 and 2
		tasks = self._queue.tasks()
		task = Task(
			title="Inserted between",
			details="Something in the middle"
		)
		task.save()
		self._queue.insert_task(task, tasks[1].id, tasks[2].id)

		tasks = self._queue.tasks()
		self.assertEqual(tasks[2].title, "Inserted between")

	def test_copy_move_task(self):
		target_queue = Queue(
			owner = self._user,
			title = "TargetQueue"
		)
		target_queue.save()

		tasks = self._queue.tasks()
		task = tasks[1]
		target_queue.append_task(task)

		# Check the source queue still contains the task
		tasks = self._queue.tasks()
		self.assertEqual(len(tasks), 3, len(tasks))

		# Check the target queue contains the task
		tasks = target_queue.tasks()
		self.assertEqual(len(tasks), 1, len(tasks))

		# Check the source queue only has 2 tasks
		self._queue.remove_task(task)
		tasks = self._queue.tasks()
		self.assertEqual(len(tasks), 2, len(tasks))

	def test_cleanup(self):
		tasks = self._queue.tasks()

		while (len(tasks)):
			tasks[0].delete()
			tasks = self._queue.tasks()

		slot_count = Slot.objects.all().count()
		self.assertEqual(slot_count, 0, slot_count)

	# TODO - test error handling where IDs don't exist


class TestApi(TestBase):
	'''
	Holds tests that call the REST API to perform functions 
	'''

	def test_get_queue(self):
		response = self._client.get("/api/queues/")
		self.assertEqual(len(response.data), 1)

	def test_create_queue(self):
		'''
		Create a queue with and retrieve via REST
		'''
		response = self._client.post(
			"/api/queues/",
			{"title": "Testing 123"}
		)
		self.assertEqual(response.status_code, 200)
		response = self._client.get("/api/queues/")
		self.assertEqual(len(response.data), 2)

	def test_create_insert_queue(self):
		'''
		Create a queue then insert some task in the middle of it and retrieve
		'''
		pass

	def test_user_permissions(self):
		pass
