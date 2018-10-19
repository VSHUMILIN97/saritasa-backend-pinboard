from django.db import migrations

# Record names for the Tag model
# Will be created everytime migrations are running
CUSTOM_TAGS = [
    'Clothes',
    'Food',
    'Auto',
    'Furniture',
    'Animals',
    'Electronics',
    'Service',
    'Business',
    'Property',
    'Apple'
]

def erase_tags(apps, schema_editor):
    """ Reverse function for erasing tags if they are already created """
    tag_model = apps.get_model("taggit", "Tag")
    db_alias = schema_editor.connection.alias
    tag_model.objects.using(db_alias).filter(name__in=CUSTOM_TAGS).delete()

def create_tags(apps, schema_editor):
    """
    Manually add all the tag fields in DB via app model

    Attributes:
    apps: Ran by Django.Current apps of the project
    schema_editor: Ran by Django.Schema of the table
    """

    tag_model = apps.get_model("taggit", "Tag")
    db_alias = schema_editor.connection.alias
    tag_model.objects.using(db_alias).bulk_create(
        (tag_model(name=tag, slug=tag.lower()) for tag in CUSTOM_TAGS)
    )

class Migration(migrations.Migration):
    dependencies = [
        ('advertisement', '0001_initial')
    ]

    """ Manually add tags to the Tag model """
    operations = [
        migrations.RunPython(
            code=create_tags,
            reverse_code=erase_tags,
        ),
    ]
