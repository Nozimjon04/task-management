from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Task, Tag


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.project = Project.objects.create(name="Test Project", owner=self.user)
        self.tag = Tag.objects.create(name="Urgent")
        self.task = Task.objects.create(
            title="Test Task",
            project=self.project,
            status=Task.Status.TODO,
            priority=Task.Priority.HIGH,
        )
        self.task.tags.add(self.tag)

    def test_project_str(self):
        self.assertEqual(str(self.project), "Test Project")

    def test_task_str(self):
        self.assertEqual(str(self.task), "Test Task")

    def test_tag_str(self):
        self.assertEqual(str(self.tag), "Urgent")

    def test_task_project_relationship(self):
        self.assertEqual(self.task.project, self.project)
        self.assertIn(self.task, self.project.tasks.all())

    def test_task_tag_many_to_many(self):
        self.assertIn(self.tag, self.task.tags.all())
        self.assertIn(self.task, self.tag.tasks.all())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.project = Project.objects.create(name="Test Project", owner=self.user)

    def test_login_required_redirect(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 302)

    def test_task_list_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_project_create(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("project_create"), {
            "name": "New Project",
            "description": "A test project",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name="New Project").exists())

    def test_task_create(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("task_create"), {
            "title": "New Task",
            "description": "A test task",
            "status": "TODO",
            "priority": "MEDIUM",
            "project": self.project.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title="New Task").exists())
