from django.conf import settings


def whatsapp_settings(request):
    """
    Make WhatsApp settings available in all templates
    """
    return {
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '919895687959'),
        'whatsapp_default_message': getattr(settings, 'WHATSAPP_DEFAULT_MESSAGE', 
                                            'Hello! I am interested in a spare part from your website.'),
    }