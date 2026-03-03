from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task, Tag
from .forms import RegisterForm, ProjectForm, TaskForm, TagForm


# ── Authentication ──────────────────────────────────────────────

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("task_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


# ── Dashboard / Task List ───────────────────────────────────────

@login_required
def task_list(request):
    tasks = Task.objects.filter(project__owner=request.user).select_related(
        "project"
    ).prefetch_related("tags")

    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    project_filter = request.GET.get("project")

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    projects = Project.objects.filter(owner=request.user)
    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "projects": projects,
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
        "current_status": status_filter,
        "current_priority": priority_filter,
        "current_project": project_filter,
    })


# ── Task CRUD ───────────────────────────────────────────────────

@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created.")
            return redirect("task_list")
    else:
        form = TaskForm(request.user)
    return render(request, "tasks/task_form.html", {"form": form, "title": "New Task"})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    if request.method == "POST":
        form = TaskForm(request.user, request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(request.user, instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "title": "Edit Task"})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


# ── Project CRUD ────────────────────────────────────────────────

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, "tasks/project_list.html", {"projects": projects})


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, "Project created.")
            return redirect("project_list")
    else:
        form = ProjectForm()
    return render(request, "tasks/project_form.html", {"form": form, "title": "New Project"})


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated.")
            return redirect("project_list")
    else:
        form = ProjectForm(instance=project)
    return render(request, "tasks/project_form.html", {"form": form, "title": "Edit Project"})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect("project_list")
    return render(request, "tasks/project_confirm_delete.html", {"project": project})


# ── Tag CRUD ────────────────────────────────────────────────────

@login_required
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, "tasks/tag_list.html", {"tags": tags})


@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created.")
            return redirect("tag_list")
    else:
        form = TagForm()
    return render(request, "tasks/tag_form.html", {"form": form, "title": "New Tag"})


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        tag.delete()
        messages.success(request, "Tag deleted.")
        return redirect("tag_list")
    return render(request, "tasks/tag_confirm_delete.html", {"tag": tag})
