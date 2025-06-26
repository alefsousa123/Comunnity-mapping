from .models import Contact

def contatos_do_usuario(user):
    if user and user.is_authenticated:
        return Contact.objects.filter(owner=user)
    return Contact.objects.none()