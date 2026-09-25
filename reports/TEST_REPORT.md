# Rapport de tests GUDLFT

Date d'exécution : 16 septembre 2026

## Périmètre

La suite vérifie les parcours nominaux et les erreurs demandées : connexion valide et
invalide, consultation publique des points, accès à une compétition, réservation réussie,
débit des points et des places, limite cumulée de 12 places, solde insuffisant, compétition
complète ou passée, quantité nulle/négative/non numérique, références inconnues et
déconnexion. Des tests supplémentaires vérifient la session, les bornes du formulaire, la
conservation de l'état après rechargement, l'échec d'écriture et six achats concurrents.

Les tests sont séparés en trois niveaux :

- 39 tests unitaires dans `tests/unit` ;
- 19 tests d'intégration dans `tests/integration` ;
- 5 tests fonctionnels dans `tests/functional`.

## Résultat

Commande exécutée :

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=server --cov-report=term-missing --cov-report=html:reports\coverage -q
```

- 63 tests réussis ;
- 0 test en échec ;
- durée : moins d'une seconde ;
- couverture de `server.py` : 96 % (objectif : au moins 60 %).

Le rapport HTML détaillé est disponible dans `reports/coverage/index.html`.

## Correspondance avec les issues GitHub

- #1 : e-mail inconnu sans plantage ;
- #2 : solde insuffisant refusé et borne du formulaire adaptée aux points ;
- #4 : limite cumulée de 12 places, y compris sur plusieurs achats ;
- #5 : compétition passée visible mais non réservable ;
- #6 : points déduits et conservés après rechargement de l'état ;
- #7 : tableau public des points ;
- #282 : impossibilité de dépasser les places restantes.
