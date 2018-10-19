from django.core.management import call_command
from django.db import migrations


def erase_social_applications(apps, schema_editor):
    """ Reverse function for erasing tags if they are already created """
    application_model = apps.get_model("oauth2_provider", "Application")
    db_alias = schema_editor.connection.alias
    application_model.objects.using(db_alias).all().delete()

def create_social_applications(apps, schema_editor):
    """
    Manually add all the tag fields in DB via app model by calling
    create_local_apps command.
    """

    call_command('create_local_apps')

class Migration(migrations.Migration):
    dependencies = [(
        'users', '0002_auto_20180813_0726',
        )
    ]

    """ Manually add apps to the Application model """
    operations = [
        migrations.RunPython(
            code=create_social_applications,
            reverse_code=erase_social_applications,
        ),
    ]
