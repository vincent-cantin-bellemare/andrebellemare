# Generated manually to add email tracking fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='last_email_datetime',
            field=models.DateTimeField(blank=True, help_text="Date et heure de la dernière tentative d'envoi d'email", null=True, verbose_name='Date dernier email'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='last_email_error',
            field=models.TextField(blank=True, help_text="Message d'erreur de la dernière tentative d'envoi d'email", verbose_name='Erreur dernier email'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='last_email_status',
            field=models.BooleanField(blank=True, help_text='True si le dernier email a été envoyé avec succès, False sinon', null=True, verbose_name='Email envoyé avec succès'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='last_email_traceback',
            field=models.TextField(blank=True, help_text="Traceback complet de la dernière erreur d'envoi d'email", verbose_name='Traceback dernier email'),
        ),
    ]
