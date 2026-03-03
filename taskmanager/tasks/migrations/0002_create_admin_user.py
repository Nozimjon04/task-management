from django.db import migrations
from django.contrib.auth.models import User


def create_admin_user(apps, schema_editor):
    """Create a default admin user if one doesn't exist."""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@taskmanager.local',
            password='password123'
        )
        print("\n✓ Admin user created: username='admin', password='password123'\n")
    else:
        print("\n✓ Admin user already exists.\n")


def delete_admin_user(apps, schema_editor):
    """Reverse: delete the admin user (optional)."""
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, delete_admin_user),
    ]
