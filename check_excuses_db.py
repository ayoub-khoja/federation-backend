#!/usr/bin/env python3
"""
Script pour vérifier les excuses dans la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import ExcuseArbitre

def check_excuses():
    """Vérifier les excuses dans la base de données"""
    print("🔍 Vérification des excuses dans la base de données...")
    print("=" * 60)
    
    # Compter toutes les excuses
    total_excuses = ExcuseArbitre.objects.count()
    print(f"📊 Total des excuses: {total_excuses}")
    
    if total_excuses == 0:
        print("❌ Aucune excuse trouvée dans la base de données")
        return
    
    # Afficher toutes les excuses
    print("\n📋 Liste des excuses:")
    for i, excuse in enumerate(ExcuseArbitre.objects.all().order_by('-created_at'), 1):
        print(f"{i}. {excuse.prenom_arbitre} {excuse.nom_arbitre}")
        print(f"   📅 Période: {excuse.date_debut} au {excuse.date_fin}")
        print(f"   📝 Cause: {excuse.cause}")
        print(f"   🕒 Créée le: {excuse.created_at}")
        print(f"   📎 Pièce jointe: {'Oui' if excuse.piece_jointe else 'Non'}")
        print()
    
    # Vérifier les excuses actives
    from django.utils import timezone
    today = timezone.now().date()
    active_excuses = ExcuseArbitre.objects.filter(
        date_debut__lte=today,
        date_fin__gte=today
    ).count()
    
    print(f"🟢 Excuses actives aujourd'hui ({today}): {active_excuses}")

if __name__ == '__main__':
    check_excuses()





