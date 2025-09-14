# Script PowerShell pour importer les grades en production
# Utilise la commande Django existante avec la configuration de production

Write-Host "🏆 IMPORTATION DES GRADES D'ARBITRAGE - PRODUCTION" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: Ce script doit être exécuté depuis le répertoire backend" -ForegroundColor Red
    exit 1
}

# Vérifier que le fichier YAML existe
if (-not (Test-Path "data/grades.yaml")) {
    Write-Host "❌ Erreur: Le fichier data/grades.yaml n'existe pas" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Configuration: PRODUCTION" -ForegroundColor Green
Write-Host "🗄️ Base de données: PostgreSQL" -ForegroundColor Green
Write-Host "📁 Fichier source: data/grades.yaml" -ForegroundColor Green
Write-Host ""

# Demander confirmation
$response = Read-Host "❓ Voulez-vous continuer avec l'importation? (oui/non)"
if ($response -notmatch "^(oui|o|yes|y)$") {
    Write-Host "❌ Importation annulée par l'utilisateur" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🚀 Lancement de l'importation..." -ForegroundColor Yellow
Write-Host ""

# Exécuter la commande Django avec la configuration de production
$env:DJANGO_SETTINGS_MODULE = "arbitrage_project.settings_production"
python manage.py import_grades --file=data/grades.yaml --force

# Vérifier le code de retour
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Importation terminée avec succès!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de l'importation!" -ForegroundColor Red
    exit 1
}
