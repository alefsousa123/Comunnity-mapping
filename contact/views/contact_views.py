from math import sin
from django.shortcuts import render, get_object_or_404
from contact.models import Contact
# from django.http import Http404


# Create your views here.
def index(request):
    """
    Render the contact page.
    Recupera todos os contatos marcados como 'show=True'
    e ordena do mais recente para o mais antigo.
    """
    contacts = (
        Contact.objects
        .filter(show=True)
        .order_by("-id")
    )

    context = {
        "contacts": contacts,
    }

    return render(
        request,
        "contact/index.html",
        context=context
    )


def contact(request, contact_id):
    single_contact = get_object_or_404(
        Contact,
        pk=contact_id,
        show=True
    )
    # single_contact = Contact.objects.filter(pk=contact_id).first()
    # if not single_contact or not single_contact.show:
    #     raise Http404("Contact not found or not available.")

    context = {
        "contact": single_contact,
    }

    return render(
        request,
        "contact/contact.html",
        context=context
    )