# Guide Complet d'Importation des Données de Référence

Ce guide vous explique comment importer toutes les données de référence (ligues et grades) en production.

## 📋 Données Disponibles

### 🏛️ Ligues d'Arbitrage
- **Fichier :** `data/ligues.yaml`
- **Modèle :** `LigueArbitrage`
- **Données :** 12 ligues tunisiennes avec régions

### 🏆 Grades d'Arbitrage
- **Fichier :** `data/grades.yaml`
- **Modèle :** `GradeArbitrage`
- **Données :** 5 grades d'arbitrage avec niveaux

## 🚀 Méthodes d'Importation

### Méthode 1 : Importation Complète (Recommandée)

```bash
# Depuis le répertoire backend
python import_all_data_production.py
```

**Avantages :**
- Importe ligues ET grades en une seule fois
- Interface utilisateur claire
- Résumé complet des résultats
- Gestion d'erreurs centralisée

### Méthode 2 : Importation Individuelle

#### Ligues uniquement :
```bash
python import_ligues_production.py
```

#### Grades uniquement :
```bash
python import_grades_production.py
```

### Méthode 3 : Commandes Django

#### Ligues :
```bash
DJANGO_SETTINGS_MODULE=arbitrage_project.settings_production python manage.py import_ligues --file=data/ligues.yaml --force
```

#### Grades :
```bash
DJANGO_SETTINGS_MODULE=arbitrage_project.settings_production python manage.py import_grades --file=data/grades.yaml --force
```

### Méthode 4 : Scripts Shell

#### Sur Linux/Mac :
```bash
# Ligues
chmod +x run_import_ligues_production.sh
./run_import_ligues_production.sh

# Grades
chmod +x run_import_grades_production.sh
./run_import_grades_production.sh
```

#### Sur Windows :
```powershell
# Ligues
.\run_import_ligues_production.ps1

# Grades
.\run_import_grades_production.ps1
```

## 📊 Résultats Attendus

### Après Importation des Ligues :
- **12 ligues** créées/mises à jour
- Ligues triées par ordre et nom
- Toutes les ligues marquées comme actives

### Après Importation des Grades :
- **5 grades** créés/mis à jour
- Grades triés par ordre, niveau et nom
- Tous les grades marqués comme actifs

## 🔍 Vérification Post-Importation

### Via l'Interface d'Administration Django :
1. Connectez-vous à l'admin Django
2. Vérifiez les sections :
   - "Ligues d'arbitrage"
   - "Grades d'arbitrage"

### Via l'API :
```bash
# Ligues
curl -X GET "https://federation-backend.onrender.com/api/ligues/"

# Grades (si API disponible)
curl -X GET "https://federation-backend.onrender.com/api/grades/"
```

## ⚠️ Points d'Attention

1. **Sauvegarde :** Effectuez une sauvegarde de la base de données avant l'importation
2. **Doublons :** Les scripts gèrent automatiquement les doublons
3. **Ordre :** Les données sont triées selon les champs `ordre` définis
4. **Activation :** Seules les données avec `is_active: true` sont marquées comme actives
5. **Codes uniques :** Les grades doivent avoir des codes uniques

## 🐛 Dépannage

### Erreur de connexion à la base de données
```bash
# Vérifier les variables d'environnement
echo $DB_NAME
echo $DB_USER
echo $DB_HOST
echo $DB_PASSWORD
```

### Erreur de fichier YAML
```bash
# Vérifier la syntaxe YAML
python -c "import yaml; yaml.safe_load(open('data/ligues.yaml'))"
python -c "import yaml; yaml.safe_load(open('data/grades.yaml'))"
```

### Erreur de modèle manquant
```bash
# Vérifier que les modèles existent
python manage.py shell -c "from accounts.models import LigueArbitrage, GradeArbitrage; print('Modèles OK')"
```

## 📝 Logs et Monitoring

Les logs d'importation sont affichés dans la console avec :
- ✅ Succès (création/mise à jour)
- 🔄 Mise à jour d'éléments existants
- ⚠️ Éléments ignorés
- ❌ Erreurs

## 🔄 Mise à Jour des Données

Pour mettre à jour les données existantes :

1. Modifiez les fichiers YAML correspondants
2. Relancez l'importation avec l'option `--force`
3. Les données existantes seront mises à jour

## 🏗️ Prochaines Étapes

Après l'importation des données de référence, vous pourrez :

1. **Créer des migrations** pour les nouveaux modèles
2. **Mettre à jour les modèles** Arbitre et Commissaire pour utiliser les ForeignKey
3. **Migrer les données existantes** vers les nouveaux modèles
4. **Tester les fonctionnalités** avec les nouvelles données

## 📞 Support

En cas de problème :
1. Vérifiez la configuration de la base de données
2. Vérifiez la syntaxe des fichiers YAML
3. Vérifiez les permissions d'accès aux fichiers
4. Consultez les logs d'erreur détaillés
5. Vérifiez que les modèles existent dans la base de données
