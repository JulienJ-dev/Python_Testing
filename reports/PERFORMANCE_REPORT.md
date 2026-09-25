# Rapport de performances GUDLFT

Date d'exécution : 16 septembre 2026

## Protocole

Locust 2.46.5 a sollicité l'application locale pendant 15 secondes avec les 6 utilisateurs
simultanés demandés. Chaque utilisateur effectue un achat d'une place, puis le scénario
charge la liste des compétitions et le tableau public des points. Le serveur a utilisé un
fichier d'état temporaire isolé des données habituelles. Les seuils sont de 5 secondes pour
la liste et de 2 secondes pour l'achat qui met à jour les points.

Commande exécutée :

```powershell
.\.venv\Scripts\python.exe -m locust -f locustfile.py --headless --users 6 --spawn-rate 6 --run-time 15s --host http://127.0.0.1:5002 --csv reports\performance\locust --html reports\performance\locust-report.html
```

## Résultats

| Requête | Requêtes | Échecs | Moyenne | Maximum | Seuil |
|---|---:|---:|---:|---:|---:|
| Liste des compétitions | 72 | 0 | 2,70 ms | 3,64 ms | 5 000 ms |
| Mise à jour des points (achat) | 6 | 0 | 11,92 ms | 14,85 ms | 2 000 ms |
| Tableau public des points | 18 | 0 | 2,33 ms | 3,38 ms | - |
| Connexion initiale | 6 | 0 | 20,39 ms | 24,84 ms | - |
| Total (instantané CSV) | 102 | 0 | 4,22 ms | 24,84 ms | - |

Les six achats ont été confirmés et l'état enregistré montre bien six points et six places
déduits, avec 0 % d'erreur. Le tableau reprend le dernier instantané du CSV ; le résumé final
en console compte 107 requêtes, car quelques requêtes ont eu lieu après cet instantané.
Le rapport interactif est dans `reports/performance/locust-report.html` et les mesures brutes
sont dans les fichiers CSV du même dossier. Ces résultats concernent le petit jeu de données
du prototype sur le serveur de développement local, pas un déploiement de production.
