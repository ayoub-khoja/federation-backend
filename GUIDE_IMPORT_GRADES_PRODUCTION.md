# Guide d'Importation des Grades en Production

Ce guide vous explique comment importer les grades d'arbitrage depuis le fichier YAML vers la base de données de production.

## 📋 Prérequis

1. **Accès à l'environnement de production**
2. **Variables d'environnement configurées** pour la base de données PostgreSQL
3. **Fichier YAML des grades** présent dans `backend/data/grades.yaml`

## 🗂️ Structure du Fichier YAML

Le fichier `data/grades.yaml` doit contenir la structure suivante :

```yaml
grades:
  - nom: "Candidat"
    code: "candidat"
    description: "Grade de débutant pour les nouveaux arbitres"
    niveau: 1
    ordre: 1
    is_active: true
  
  - nom: "3ème Série"
    code: "3eme_serie"
    description: "Troisième série d'arbitrage"
    niveau: 2
    ordre: 2
    is_active: true
    
  # ... autres grades
```

## 🚀 Méthodes d'Importation

### Méthode 1 : Script Python Direct (Recommandé)

```bash
# Depuis le répertoire backend
python import_grades_production.py
```

**Avantages :**
- Interface utilisateur claire
- Gestion d'erreurs complète
- Confirmation avant exécution
- Résumé détaillé

### Méthode 2 : Commande Django

```bash
# Depuis le répertoire backend
DJANGO_SETTINGS_MODULE=arbitrage_project.settings_production python manage.py import_grades --file=data/grades.yaml --force
```

**Avantages :**
- Utilise la commande Django existante
- Plus simple pour l'automatisation

### Méthode 3 : Scripts Shell

#### Sur Linux/Mac :
```bash
chmod +x run_import_grades_production.sh
./run_import_grades_production.sh
```

#### Sur Windows :
```powershell
.\run_import_grades_production.ps1
```

## ⚙️ Configuration de Production

Le script utilise automatiquement la configuration de production définie dans `arbitrage_project/settings_production.py` :

- **Base de données :** PostgreSQL
- **Configuration :** `arbitrage_project.settings_production`
- **Mode DEBUG :** `False`

## 📊 Résultat de l'Importation

Après l'importation, vous verrez :

1. **Nombre de grades créés**
2. **Nombre de grades mis à jour**
3. **Nombre de grades ignorés**
4. **Total des grades en base**
5. **Liste des grades actifs avec leurs niveaux**

## 🔍 Vérification Post-Importation

### Via l'Interface d'Administration Django :
1. Connectez-vous à l'admin Django
2. Allez dans "Grades d'arbitrage"
3. Vérifiez que tous les grades sont présents

### Via l'API :
```bash
curl -X GET "https://federation-backend.onrender.com/api/grades/"
```

## ⚠️ Points d'Attention

1. **Sauvegarde :** Effectuez une sauvegarde de la base de données avant l'importation
2. **Doublons :** Le script gère automatiquement les doublons (mise à jour si existe)
3. **Ordre :** Les grades sont triés par le champ `ordre`, puis par `niveau`, puis par nom
4. **Activation :** Seuls les grades avec `is_active: true` sont marqués comme actifs
5. **Codes uniques :** Chaque grade doit avoir un code unique

## 🐛 Dépannage

### Erreur de connexion à la base de données
```bash
# Vérifier les variables d'environnement
echo $DB_NAME
echo $DB_USER
echo $DB_HOST
```

### Erreur de fichier YAML
```bash
# Vérifier la syntaxe YAML
python -c "import yaml; yaml.safe_load(open('data/grades.yaml'))"
```

### Erreur de permissions
```bash
# Vérifier les permissions sur les fichiers
ls -la import_grades_production.py
ls -la data/grades.yaml
```

## 📝 Logs et Monitoring

Les logs d'importation sont affichés dans la console. Pour un monitoring plus avancé, consultez les logs de l'application sur votre plateforme de déploiement.

## 🔄 Mise à Jour des Grades

Pour mettre à jour les grades existants :

1. Modifiez le fichier `data/grades.yaml`
2. Relancez l'importation avec l'option `--force`
3. Les grades existants seront mis à jour avec les nouvelles données

## 🏗️ Migration des Données Existantes

Si vous avez des arbitres et commissaires existants avec des grades en format texte, vous devrez :

1. **Créer une migration** pour ajouter le champ ForeignKey vers GradeArbitrage
2. **Migrer les données** existantes vers le nouveau modèle
3. **Mettre à jour les modèles** Arbitre et Commissaire

## 📞 Support

En cas de problème, vérifiez :
1. La configuration de la base de données
2. La syntaxe du fichier YAML
3. Les permissions d'accès aux fichiers
4. Les logs d'erreur détaillés
5. L'existence du modèle GradeArbitrage dans la base de données
