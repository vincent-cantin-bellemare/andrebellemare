from django.db import migrations


def update_faqs(apps, schema_editor):
    FAQ = apps.get_model('contact', 'FAQ')

    FAQ.objects.filter(
        question='Comment puis-je acheter une toile?'
    ).update(
        answer='Pour acquérir une toile, contactez la Fondation de la Maison du Père au 514-845-0168 poste 358.'
    )

    FAQ.objects.filter(
        question='Pourquoi le paiement se fait-il par don à la Maison du Père?'
    ).update(
        answer=(
            "C'est ma façon de donner un sens plus profond à mon art. "
            "Chaque toile vendue permet d'aider les personnes en situation "
            "d'itinérance à Montréal.\n\n"
            "Vous repartez avec une œuvre originale. Tout le monde y gagne!"
        )
    )

    FAQ.objects.filter(
        question="Livrez-vous à l'extérieur de Boucherville?"
    ).update(is_active=False)


def reverse_faqs(apps, schema_editor):
    FAQ = apps.get_model('contact', 'FAQ')

    FAQ.objects.filter(
        question='Comment puis-je acheter une toile?'
    ).update(
        answer=(
            'Pour acquérir une toile, cliquez sur le bouton "Acheter" de l\'œuvre '
            "qui vous intéresse et remplissez le formulaire avec vos coordonnées. "
            "Je vous contacterai ensuite pour organiser les détails.\n\n"
            "Le montant affiché correspond au don à effectuer à la Maison du Père. "
            "Une fois le don effectué et le reçu présenté, la toile vous sera remise."
        )
    )

    FAQ.objects.filter(
        question='Pourquoi le paiement se fait-il par don à la Maison du Père?'
    ).update(
        answer=(
            "C'est ma façon de donner un sens plus profond à mon art. "
            "Chaque toile vendue permet d'aider les personnes en situation "
            "d'itinérance à Montréal.\n\n"
            "Vous bénéficiez d'un reçu fiscal pour votre don, et vous repartez "
            "avec une œuvre originale. Tout le monde y gagne!"
        )
    )

    FAQ.objects.filter(
        question="Livrez-vous à l'extérieur de Boucherville?"
    ).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_faqs, reverse_faqs),
    ]
