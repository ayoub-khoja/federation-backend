"""
Service d'envoi d'emails pour la réinitialisation de mot de passe
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class PasswordResetEmailService:
    """Service pour l'envoi d'emails de réinitialisation de mot de passe"""
    
    @staticmethod
    def send_password_reset_email(user, token, request=None):
        """
        Envoyer un email de réinitialisation de mot de passe
        
        Args:
            user: L'utilisateur (Arbitre, Commissaire ou Admin)
            token: Le token de réinitialisation
            request: La requête HTTP (optionnel, pour récupérer l'IP)
        
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        try:
            # Récupérer les paramètres de configuration
            email_settings = getattr(settings, 'PASSWORD_RESET_SETTINGS', {})
            subject_prefix = email_settings.get('EMAIL_SUBJECT_PREFIX', '[Fédération Tunisienne de Football] ')
            frontend_url = email_settings.get('FRONTEND_RESET_URL', 'https://votre-frontend.com/reset-password/')
            
            # Déterminer le type d'utilisateur
            user_type = type(user).__name__.lower()
            user_type_display = {
                'arbitre': 'Arbitre',
                'commissaire': 'Commissaire',
                'admin': 'Administrateur'
            }.get(user_type, 'Utilisateur')
            
            # Construire l'URL de réinitialisation
            reset_url = f"{frontend_url}?token={token.token}"
            
            # Données pour le template
            context = {
                'user': user,
                'user_type': user_type_display,
                'user_name': user.get_full_name(),
                'reset_url': reset_url,
                'otp_code': token.otp_code,
                'token_expiry_minutes': email_settings.get('TOKEN_EXPIRY_MINUTES', 5),
                'site_name': 'Fédération Tunisienne de Football',
                'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@arbitrage.tn'),
            }
            
            # Sujet de l'email
            subject = f"{subject_prefix}Réinitialisation de votre mot de passe - Code OTP: {token.otp_code}"
            
            # Corps de l'email en HTML
            html_message = PasswordResetEmailService._render_html_email(context)
            
            # Corps de l'email en texte brut
            plain_message = PasswordResetEmailService._render_plain_email(context)
            
            # Envoyer l'email
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@arbitrage.tn')
            recipient_list = [user.email]
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de réinitialisation envoyé avec succès à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation à {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def _render_html_email(context):
        """Rendre le template HTML de l'email"""
        html_template = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Réinitialisation de mot de passe</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #1e3a8a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }
                .content {
                    background-color: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }
                .button {
                    display: inline-block;
                    background-color: #dc2626;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 20px 0;
                }
                .button:hover {
                    background-color: #b91c1c;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }
                .warning {
                    background-color: #fef3c7;
                    border: 1px solid #f59e0b;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ site_name }}</h1>
                <h2>Réinitialisation de mot de passe</h2>
            </div>
            
            <div class="content">
                <p>Bonjour <strong>{{ user_name }}</strong>,</p>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte {{ user_type }}.</p>
                
                <div class="warning">
                    <strong>🔐 Code OTP de sécurité :</strong>
                    <div style="font-size: 24px; font-weight: bold; color: #dc2626; text-align: center; margin: 15px 0; padding: 15px; background-color: #fef2f2; border: 2px solid #dc2626; border-radius: 8px;">
                        {{ otp_code }}
                    </div>
                </div>
                
                <p>Pour réinitialiser votre mot de passe, vous devez :</p>
                <ol>
                    <li><strong>Entrer le code OTP ci-dessus</strong> dans l'application</li>
                    <li><strong>Cliquer sur le lien</strong> ci-dessous pour accéder au formulaire</li>
                </ol>
                
                <div style="text-align: center;">
                    <a href="{{ reset_url }}" class="button">Accéder au formulaire de réinitialisation</a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important :</strong>
                    <ul>
                        <li>Le code OTP et le lien sont valides pendant {{ token_expiry_minutes }} minutes</li>
                        <li>Vous devez utiliser le code OTP ET le lien pour réinitialiser votre mot de passe</li>
                        <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                        <li>Ne partagez jamais ce code OTP ou ce lien avec d'autres personnes</li>
                    </ul>
                </div>
                
                <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                <p style="word-break: break-all; background-color: #e5e7eb; padding: 10px; border-radius: 4px;">
                    {{ reset_url }}
                </p>
                
                <p>Si vous rencontrez des problèmes, contactez notre support à : <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
            </div>
            
            <div class="footer">
                <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                <p>&copy; 2024 {{ site_name }}. Tous droits réservés.</p>
            </div>
        </body>
        </html>
        """
        
        # Remplacer les variables dans le template
        for key, value in context.items():
            html_template = html_template.replace(f'{{{{ {key} }}}}', str(value))
        
        return html_template
    
    @staticmethod
    def _render_plain_email(context):
        """Rendre le template texte de l'email"""
        plain_template = f"""
{context['site_name']} - Réinitialisation de mot de passe

Bonjour {context['user_name']},

Vous avez demandé la réinitialisation de votre mot de passe pour votre compte {context['user_type']}.

🔐 CODE OTP DE SÉCURITÉ : {context['otp_code']}

Pour réinitialiser votre mot de passe, vous devez :
1. Entrer le code OTP ci-dessus dans l'application
2. Cliquer sur le lien suivant pour accéder au formulaire :
{context['reset_url']}

⚠️ IMPORTANT :
- Le code OTP et le lien sont valides pendant {context['token_expiry_minutes']} minutes
- Vous devez utiliser le code OTP ET le lien pour réinitialiser votre mot de passe
- Si vous n'avez pas demandé cette réinitialisation, ignorez cet email
- Ne partagez jamais ce code OTP ou ce lien avec d'autres personnes

Si vous rencontrez des problèmes, contactez notre support à : {context['support_email']}

---
Cet email a été envoyé automatiquement, merci de ne pas y répondre.
© 2024 {context['site_name']}. Tous droits réservés.
        """
        
        return plain_template.strip()
