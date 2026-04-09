# Cabinet d'Avocat - Système de Gestion

Un système de gestion moderne pour cabinet d'avocat développé avec Django.

## Fonctionnalités

- Gestion des clients
- Gestion des dossiers
- Gestion des rendez-vous
- Gestion des documents
- Interface utilisateur intuitive
- Système d'authentification sécurisé

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- virtualenv (recommandé)

## Installation

1. Cloner le dépôt :
```bash
git clone [url-du-depot]
cd cabinet_avocat
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
- Copier le fichier `.env.example` vers `.env`
- Modifier les valeurs dans `.env` selon votre environnement

5. Appliquer les migrations :
```bash
python manage.py migrate
```

6. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

## Lancement du serveur de développement

```bash
python manage.py runserver
```

Le site sera accessible à l'adresse : http://127.0.0.1:8000/

## Déploiement en production

Pour le déploiement en production, assurez-vous de :

1. Mettre DEBUG=False dans le fichier .env
2. Configurer un serveur web (nginx/Apache) avec gunicorn
3. Utiliser une base de données robuste (PostgreSQL recommandé)
4. Configurer correctement les paramètres de sécurité
5. Mettre en place HTTPS

## Maintenance

- Effectuer régulièrement des sauvegardes de la base de données
- Mettre à jour les dépendances régulièrement
- Surveiller les logs pour détecter d'éventuels problèmes

## Support

Pour toute question ou problème, veuillez créer une issue dans le dépôt du projet. 