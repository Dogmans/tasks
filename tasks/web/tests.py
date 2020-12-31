from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient
from web.models import Queue, Slot, Task, Workspace


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

		self._client = APIClient()
		self._client.login(
			username="TestUser",
			password="12345"
		)

		self._user_two = User.objects.create_user(
			username="TestUser2",
			email="willfg@gmail.com",
			password="12345",
			first_name="Test2",
			last_name="User2",
		)
		self._user_two.save()

		self._client_two = APIClient()
		self._client_two.login(
			username="TestUser2",
			password="12345"
		)

		self._workspace = Workspace(
			owner = self._user,
			title = "TestWorkspace"
		)
		self._workspace.save()

		self._queue = Queue(
			owner = self._user,
			title = "TestQueue",
			workspace = self._workspace
		)
		self._queue.save()

		for title in ["TestTask1", "TestTask2", "TestTask3"]:
			task = Task(
				title=title,
				details="Something",
				owner=self._user
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
			details="Something in the middle",
			owner=self._user
		)
		task.save()
		self._queue.insert_task(task, tasks[1].id, tasks[2].id)

		tasks = self._queue.tasks()
		self.assertEqual(tasks[2].title, "Inserted between")

	def test_copy_move_task(self):
		target_queue = Queue(
			owner = self._user,
			title = "TargetQueue",
			workspace = self._workspace
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

	def test_task_cleanup(self):
		tasks = self._queue.tasks()

		while (len(tasks)):
			tasks[0].delete()
			tasks = self._queue.tasks()

		slot_count = Slot.objects.all().count()
		self.assertEqual(slot_count, 0, slot_count)

	def test_workspace_cleanup(self):
		self._workspace.delete()

		slot_count = Slot.objects.all().count()
		self.assertEqual(slot_count, 0, slot_count)

		queue_count = Queue.objects.all().count()
		self.assertEqual(queue_count, 0, queue_count)

		task_count = Task.objects.all().count()
		self.assertEqual(task_count, 0, task_count)

	# TODO - test queue deletion - it will delete slots but not orphaned tasks!
	# TODO - when queue is deleted then it should actually search for these too
	# TODO - test error handling where IDs don't exist


class TestApi(TestBase):
	'''
	Holds tests that call the REST API to perform functions 
	'''

	def test_create_retrieve_task(self):
		'''
		Create and retrieve task
		'''
		response = self._client.post(
			"/api/tasks/",
			{
				"title": "Testing 123",
				"details": "Test details"
			},
			format="json"
		)
		task_id = response.data["id"]
		response = self._client.get("/api/tasks/%s/" % task_id)
		self.assertEqual(response.data["id"], task_id)

	def test_get_queues(self):
		response = self._client.get("/api/workspaces/%s/queues/" % self._workspace.id)
		self.assertEqual(len(response.data), 1)

	def test_queue_get_tasks(self):
		response = self._client.get("/api/queues/%s/tasks/" % self._queue.id)
		self.assertEqual(len(response.data), 3)

	def test_update_queue(self):
		response = self._client.put(
			"/api/queues/" + str(self._queue.id) + "/",
			{
				"title": "Testing 456"
			},
			format="json"
		)
		# Check it was updated and not created
		self.assertEqual(response.status_code, 200, response.data)
		self.assertEqual(Queue.objects.all().count(), 1, Queue.objects.all())

	def test_create_retrieve_queues(self):
		'''
		Create a queue with and retrieve via REST
		'''
		response = self._client.post(
			"/api/workspaces/%s/queues/" % self._workspace.id,
			{"title": "Testing 123"},
			format="json"
		)
		# Created successfully
		self.assertEqual(response.status_code, 201, response.data)

		# Check we now have 2 queues
		response = self._client.get("/api/workspaces/%s/queues/" % self._workspace.id)
		self.assertEqual(len(response.data), 2)

	def test_queue_append_task(self):
		'''
		Create a task then append to a queue
		'''
		response = self._client.post(
			"/api/tasks/",
			{
				"title": "Task 123",
				"details": "Task 123 details"
			},
			format="json"
		)
		# Created successfully
		self.assertTrue(response.data, response)
		self.assertEqual(response.status_code, 201, response.data)
		task_id = response.data["id"]

		# Now append to the queue
		queue_id = self._queue.id
		response = self._client.post(
			"/api/queues/%s/tasks/" % queue_id,
			{
				"task_id": task_id
			},
			format="json"
		)
		# Inserted successfully
		self.assertEqual(response.status_code, 201, response.data)

		# Now query for all tasks under this queue (it's returned above too)
		response = self._client.get(
			"/api/queues/%s/tasks/" % queue_id,
			format="json"
		)
		# Check that our task is in there
		self.assertEqual(response.status_code, 200, response.data)

	def test_queue_insert_task(self):
		# TODO - test inserting a task between 2 others
		pass

	def test_queue_remove_task(self):
		'''
		Remove an existing task from the queue
		'''
		task_to_remove = self._queue.tasks()[1]
		response = self._client.delete(
			"/api/queues/%s/tasks/%s/" % (self._queue.id, task_to_remove.id),
			format="json"
		)
		self.assertEqual(response.status_code, 204, response)
		self.assertEqual(len(self._queue.tasks()), 2, response)

	def test_queue_anonymous_user(self):
		'''
		Test that anonymous users are handled correctly
		'''
		response = self._client.get("/api/queues/")
		self.assertEqual(len(response.data), 1)
		self._client.logout()
		response = self._client.get("/api/queues/")
		self.assertEqual(response.status_code, 403, response)

	def test_workspace_add_queue(self):
		'''
		Test that queue can be added to workspace
		'''
		response = self._client.post(
			"/api/workspaces/%s/queues/" % self._workspace.id,
			{
				"title": "Another queue"
			},
			format="json"
		)
		self.assertEqual(self._workspace.queue_set.all().count(), 2)

	def test_workspace_remove_queue(self):
		'''
		Test that queue can be removed from workspace
		'''
		response = self._client.delete(
			"/api/workspaces/%s/queues/%s/" % (self._workspace.id, self._queue.id)
		)
		self.assertEqual(self._workspace.queue_set.all().count(), 0)

	def test_user_permissions(self):
		'''
		Make sure user 2 does not have access to user 1 objects
		'''
		response = self._client.get("/api/queues/")
		self.assertEqual(len(response.data), 1)

		# Check queues not visible to second user
		response = self._client_two.get("/api/queues/")
		self.assertEqual(len(response.data), 0)

		# Check 2nd user can't get 1st user's task
		response = self._client.post(
			"/api/tasks/",
			{
				"title": "Task 123",
				"details": "Task 123 details"
			},
			format="json"
		)
		task_id = response.data["id"]

		response = self._client.get(
			"/api/tasks/%s/" % task_id,
			format="json"
		)
		self.assertEqual(response.status_code, 200, response)

		response = self._client_two.get(
			"/api/tasks/%s/" % task_id,
			format="json"
		)
		self.assertEqual(response.status_code, 404, response)

		# Check 2nd user can't do anything to the wrong queue
		# TODO - GET / POST / DELETE etc.


