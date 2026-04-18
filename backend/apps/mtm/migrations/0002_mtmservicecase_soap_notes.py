from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mtmservicecase',
            name='soap_notes',
            field=models.JSONField(blank=True, default=dict, help_text='结构化的 SOAP 药历记录', verbose_name='SOAP 药历'),
        ),
    ]
