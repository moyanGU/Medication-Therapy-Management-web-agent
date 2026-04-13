# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medicines", "0002_alter_medicine_image_url"),
    ]

    operations = [
        migrations.RenameField(
            model_name="medicine",
            old_name="image_url",
            new_name="image_path",
        ),
        migrations.AlterField(
            model_name="medicine",
            name="image_path",
            field=models.CharField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name="药品图片路径",
                help_text="药品图片的服务器存储路径",
            ),
        ),
    ]
