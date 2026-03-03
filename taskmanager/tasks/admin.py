from django.contrib import admin
from .models import Project, Task, Tag


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "updated_at")
    list_filter = ("owner", "created_at")
    search_fields = ("name", "description")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "due_date", "created_at")
    list_filter = ("status", "priority", "project", "tags")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)
