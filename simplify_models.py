#!/usr/bin/env python
"""
Script pour simplifier les modèles en rendant les champs optionnels
"""
import re

def simplify_models():
    """Simplifier les modèles en rendant les champs optionnels"""
    
    # Lire le fichier models.py
    with open('accounts/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer les champs problématiques
    replacements = [
        # birth_date
        (r'birth_date = models\.DateField\(verbose_name="Date de naissance"\)',
         'birth_date = models.DateField(verbose_name="Date de naissance", null=True, blank=True)'),
        
        # birth_place
        (r'birth_place = models\.CharField\(max_length=100, verbose_name="Lieu de naissance"\)',
         'birth_place = models.CharField(max_length=100, verbose_name="Lieu de naissance", null=True, blank=True)'),
        
        # address
        (r'address = models\.TextField\(verbose_name="Adresse"\)',
         'address = models.TextField(verbose_name="Adresse", null=True, blank=True)'),
    ]
    
    # Appliquer les remplacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Écrire le fichier modifié
    with open('accounts/models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Modèles simplifiés avec succès!")
    print("📋 Champs rendus optionnels:")
    print("   - birth_date (null=True, blank=True)")
    print("   - birth_place (null=True, blank=True)")
    print("   - address (null=True, blank=True)")

if __name__ == "__main__":
    simplify_models()
