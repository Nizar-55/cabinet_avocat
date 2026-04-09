import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')
django.setup()

from utilisateurs.models import Utilisateur

def setup_admin():
    try:
        admin = Utilisateur.objects.get(username='admin')
        admin.role = 'avocat'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"Updated admin user: {admin.username} (role: {admin.role})")
    except Utilisateur.DoesNotExist:
        admin = Utilisateur.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin',
            role='avocat'
        )
        print(f"Created admin user: {admin.username} (role: {admin.role})")

if __name__ == '__main__':
    setup_admin() 