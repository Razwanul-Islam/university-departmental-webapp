from django.db import migrations


def promote_admins(apps, schema_editor):
    apps.get_model('account', 'User').objects.filter(is_admin=True).update(user_type='H')


class Migration(migrations.Migration):
    dependencies = [('account', '0003_alter_user_user_type')]
    operations = [migrations.RunPython(promote_admins, migrations.RunPython.noop)]
