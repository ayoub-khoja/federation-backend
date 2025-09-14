# Guide d'Importation des Ligues en Production

Ce guide vous explique comment importer les ligues d'arbitrage depuis le fichier YAML vers la base de données de production.

## 📋 Prérequis

1. **Accès à l'environnement de production**
2. **Variables d'environnement configurées** pour la base de données PostgreSQL
3. **Fichier YAML des ligues** présent dans `backend/data/ligues.yaml`

## 🗂️ Structure du Fichier YAML

Le fichier `data/ligues.yaml` doit contenir la structure suivante :

```yaml
ligues_tunisiennes:
  - code: "tunis"
    nom: "Ligue de Tunis"
    region: "Grand Tunis"
    active: true
    ordre: 1
    
  - code: "nabeul"
    nom: "Ligue de Nabeul"
    region: "Cap Bon"
    active: true
    ordre: 2
    
  # ... autres ligues
```

## 🚀 Méthodes d'Importation

### Méthode 1 : Script Python Direct (Recommandé)

```bash
# Depuis le répertoire backend
python import_ligues_production.py
```

**Avantages :**
- Interface utilisateur claire
- Gestion d'erreurs complète
- Confirmation avant exécution
- Résumé détaillé

### Méthode 2 : Commande Django

```bash
# Depuis le répertoire backend
DJANGO_SETTINGS_MODULE=arbitrage_project.settings_production python manage.py import_ligues --file=data/ligues.yaml --force
```

**Avantages :**
- Utilise la commande Django existante
- Plus simple pour l'automatisation

### Méthode 3 : Scripts Shell

#### Sur Linux/Mac :
```bash
chmod +x run_import_ligues_production.sh
./run_import_ligues_production.sh
```

#### Sur Windows :
```powershell
.\run_import_ligues_production.ps1
```

## ⚙️ Configuration de Production

Le script utilise automatiquement la configuration de production définie dans `arbitrage_project/settings_production.py` :

- **Base de données :** PostgreSQL
- **Configuration :** `arbitrage_project.settings_production`
- **Mode DEBUG :** `False`

## 📊 Résultat de l'Importation

Après l'importation, vous verrez :

1. **Nombre de ligues créées**
2. **Nombre de ligues mises à jour**
3. **Nombre de ligues ignorées**
4. **Total des ligues en base**
5. **Liste des ligues actives**

## 🔍 Vérification Post-Importation

### Via l'Interface d'Administration Django :
1. Connectez-vous à l'admin Django
2. Allez dans "Ligues d'arbitrage"
3. Vérifiez que toutes les ligues sont présentes

### Via l'API :
```bash
curl -X GET "https://federation-backend.onrender.com/api/ligues/"
```

## ⚠️ Points d'Attention

1. **Sauvegarde :** Effectuez une sauvegarde de la base de données avant l'importation
2. **Doublons :** Le script gère automatiquement les doublons (mise à jour si existe)
3. **Ordre :** Les ligues sont triées par le champ `ordre` puis par nom
4. **Activation :** Seules les ligues avec `active: true` sont marquées comme actives

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
python -c "import yaml; yaml.safe_load(open('data/ligues.yaml'))"
```

### Erreur de permissions
```bash
# Vérifier les permissions sur les fichiers
ls -la import_ligues_production.py
ls -la data/ligues.yaml
```

## 📝 Logs et Monitoring

Les logs d'importation sont affichés dans la console. Pour un monitoring plus avancé, consultez les logs de l'application sur votre plateforme de déploiement.

## 🔄 Mise à Jour des Ligues

Pour mettre à jour les ligues existantes :

1. Modifiez le fichier `data/ligues.yaml`
2. Relancez l'importation avec l'option `--force`
3. Les ligues existantes seront mises à jour avec les nouvelles données

## 📞 Support

En cas de problème, vérifiez :
1. La configuration de la base de données
2. La syntaxe du fichier YAML
3. Les permissions d'accès aux fichiers
4. Les logs d'erreur détaillés
