from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os
from utilisateurs.models import LawCategory

class Command(BaseCommand):
    help = 'Creates initial law categories with icons'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Droit des affaires',
                'description': 'Conseil et assistance juridique pour les entreprises, contrats commerciaux, droit des sociétés.',
                'icon': 'business_law.jpg',
                'order': 1
            },
            {
                'name': 'Droit immobilier',
                'description': 'Transactions immobilières, baux, copropriété, construction.',
                'icon': 'real_estate_law.jpg',
                'order': 2
            },
            {
                'name': 'Droit de la famille',
                'description': 'Divorce, garde d\'enfants, succession, adoption.',
                'icon': 'family_law.jpg',
                'order': 3
            },
            {
                'name': 'Droit du travail',
                'description': 'Relations employeur-employé, contrats de travail, litiges sociaux.',
                'icon': 'labor_law.jpg',
                'order': 4
            },
            {
                'name': 'Droit pénal',
                'description': 'Défense pénale, assistance aux victimes.',
                'icon': 'criminal_law.jpg',
                'order': 5
            },
            {
                'name': 'Droit administratif',
                'description': 'Litiges avec l\'administration, marchés publics.',
                'icon': 'administrative_law.jpg',
                'order': 6
            }
        ]

        for category_data in categories:
            category, created = LawCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'order': category_data['order']
                }
            )
            
            if created:
                icon_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'law_categories', category_data['icon'])
                if os.path.exists(icon_path):
                    with open(icon_path, 'rb') as icon_file:
                        category.icon.save(category_data['icon'], File(icon_file), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Icon not found for category: {category.name}')) 