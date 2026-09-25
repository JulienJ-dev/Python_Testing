# GUDLFT - plateforme régionale de réservation

Ce projet Flask est un prototype léger permettant aux secrétaires de clubs de consulter les
compétitions et d'utiliser leurs points pour réserver des places. Une page publique affiche
également le solde de tous les clubs.

## Fonctionnalités

- connexion par l'adresse e-mail d'un club et message clair en cas d'adresse inconnue ;
- liste des compétitions et réservation d'une compétition à venir ;
- débit d'un point par place sur le club et d'une place sur la compétition ;
- refus des quantités invalides, des compétitions passées, du dépassement des points ou des
  places disponibles et de plus de 12 places au total par club et par compétition ;
- formulaire limité automatiquement par le solde, les places restantes et le quota du club ;
- réservations réservées au club connecté et protégées contre les achats concurrents ;
- tableau public, en lecture seule, accessible à l'adresse `/pointsDisplay` ;
- déconnexion et gestion des références inconnues sans plantage.

`clubs.json` et `competitions.json` servent de données initiales. Au premier achat,
l'application crée `state.json` pour conserver ensemble les points, les places restantes et
le nombre de places déjà achetées par club. Les achats restent donc présents après un
redémarrage. Pour repartir des données initiales, supprimez `state.json` lorsque le serveur
est arrêté. Ce fichier est ignoré par Git et ne doit pas être supprimé en cours d'utilisation.

## Installation sous Windows

Python 3.10 ou plus récent est recommandé.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Lancer l'application

```powershell
python -m flask --app server run
```

Ouvrez ensuite `http://127.0.0.1:5000`. Une adresse valide est
`john@simplylift.co` ; les autres adresses se trouvent dans `clubs.json`.
Pour un déploiement hors de la machine locale, définissez `FLASK_SECRET_KEY` dans
l'environnement. Cette démonstration identifie le club par son e-mail seul : elle ne fournit
pas d'authentification par mot de passe.

## Tests et couverture

```powershell
python -m pytest --cov=server --cov-report=term-missing --cov-report=html:reports\coverage
```

Les tests sont rangés par niveau dans `tests/unit`, `tests/integration` et
`tests/functional`. Le dernier résultat validé compte 63 tests réussis et 96 % de
couverture. Le compte rendu se trouve dans `reports/TEST_REPORT.md`.

## Test de performances

Le scénario réalise six vrais achats. Pour éviter de modifier vos données de démonstration,
utilisez un fichier d'état temporaire neuf lors du lancement du serveur (changez son nom
à chaque nouvelle campagne de charge) :

```powershell
$env:GUDLFT_STATE_FILE = "$PWD\tmp\performance-state.json"
New-Item -ItemType Directory -Force tmp | Out-Null
python -m flask --app server run
```

Dans un autre terminal, lancez :

```powershell
python -m locust -f locustfile.py --headless --run-time 15s --host http://127.0.0.1:5000 --csv reports\performance\locust --html reports\performance\locust-report.html
```

Le fichier `locust.conf` définit par défaut 6 utilisateurs et un démarrage de 6 utilisateurs
par seconde. Il n'est donc pas nécessaire de répéter ces paramètres dans la commande.

Le compte rendu se trouve dans `reports/PERFORMANCE_REPORT.md`. Le scénario applique les
seuils des spécifications : 5 secondes pour la liste des compétitions et 2 secondes pour
une mise à jour réelle des points. Il utilise une réservation par utilisateur virtuel.

## Conventions

- code et noms techniques en anglais ;
- fonctions et variables en `snake_case`, constantes en majuscules ;
- un fichier de test nommé `test_*.py` par groupe de comportements ;
- branches de travail nommées `feature/...`, `bug/...` ou `improvement/...`, puis branche
  `QA` pour la revue finale.

## Ressources

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation pytest](https://docs.pytest.org/)
- [Documentation Locust](https://docs.locust.io/)
- [Dépôt de départ OpenClassrooms](https://github.com/OpenClassrooms-Student-Center/Python_Testing)
