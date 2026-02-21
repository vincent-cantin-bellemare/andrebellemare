from django.db import migrations, models


def migrate_available_to_maison_pere(apps, schema_editor):
    Painting = apps.get_model('gallery', 'Painting')
    Painting.objects.filter(status='available').update(status='available_maison_pere')


def migrate_maison_pere_to_available(apps, schema_editor):
    Painting = apps.get_model('gallery', 'Painting')
    Painting.objects.filter(
        status__in=['available_maison_pere', 'available_direct']
    ).update(status='available')


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='painting',
            name='status',
            field=models.CharField(
                choices=[
                    ('available_maison_pere', 'À vendre (Maison du Père)'),
                    ('available_direct', 'À vendre (directement)'),
                    ('sold', 'Vendu'),
                    ('not_for_sale', 'Non à vendre'),
                ],
                default='available_maison_pere',
                max_length=25,
                verbose_name='Statut',
            ),
        ),
        migrations.RunPython(
            migrate_available_to_maison_pere,
            migrate_maison_pere_to_available,
        ),
    ]
