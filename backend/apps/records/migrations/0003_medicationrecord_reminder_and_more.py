from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reminders", "0003_alter_reminder_meal_timing"),
        ("records", "0002_alter_medicationrecord_effectiveness_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicationrecord",
            name="reminder",
            field=models.ForeignKey(
                blank=True,
                help_text="若记录由提醒确认生成，则关联到对应提醒",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="medication_records",
                to="reminders.reminder",
                verbose_name="关联提醒",
            ),
        ),
        migrations.AddField(
            model_name="medicationrecord",
            name="scheduled_time",
            field=models.DateTimeField(
                blank=True, help_text="原计划的服药时间", null=True, verbose_name="计划服药时间"
            ),
        ),
        migrations.AlterField(
            model_name="medicationrecord",
            name="quantity_taken",
            field=models.PositiveIntegerField(
                help_text="本次服用的药品数量", verbose_name="服药数量"
            ),
        ),
        migrations.AddIndex(
            model_name="medicationrecord",
            index=models.Index(fields=["reminder"], name="idx_med_rec_reminder"),
        ),
        migrations.AddIndex(
            model_name="medicationrecord",
            index=models.Index(fields=["scheduled_time"], name="idx_med_rec_scheduled"),
        ),
    ]
