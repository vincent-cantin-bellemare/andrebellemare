from django.db import migrations, models


def migrate_sold_to_maison_pere(apps, schema_editor):
    Painting = apps.get_model('gallery', 'Painting')
    Painting.objects.filter(status='sold').update(status='sold_maison_pere')


def migrate_maison_pere_to_sold(apps, schema_editor):
    Painting = apps.get_model('gallery', 'Painting')
    Painting.objects.filter(status='sold_maison_pere').update(status='sold')


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_add_category_is_active'),
    ]

    operations = [
        migrations.RunPython(migrate_sold_to_maison_pere, migrate_maison_pere_to_sold),
        migrations.AddField(
            model_name='painting',
            name='purchaser_name',
            field=models.CharField(blank=True, max_length=200, verbose_name="Nom de l'acheteur"),
        ),
        migrations.AddField(
            model_name='painting',
            name='purchaser_city',
            field=models.CharField(blank=True, max_length=100, verbose_name="Ville de l'acheteur"),
        ),
        migrations.AddField(
            model_name='painting',
            name='purchase_comment',
            field=models.TextField(blank=True, verbose_name='Commentaire'),
        ),
        migrations.AddField(
            model_name='painting',
            name='purchase_date',
            field=models.DateField(blank=True, null=True, verbose_name="Date d'achat"),
        ),
        migrations.AlterField(
            model_name='painting',
            name='status',
            field=models.CharField(
                choices=[
                    ('available_maison_pere', 'À vendre (Maison du Père)'),
                    ('available_direct', 'À vendre (directement)'),
                    ('sold_maison_pere', 'Vendu (Maison du Père)'),
                    ('sold_direct', 'Vendu (vente directe)'),
                    ('not_for_sale', 'Non à vendre'),
                ],
                default='available_maison_pere',
                max_length=25,
                verbose_name='Statut',
            ),
        ),
    ]
