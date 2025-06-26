# filepath: c:\Users\lefaz\Documents\GitHub\AgendaTelefonica\contact\widgets.py
from django_select2.forms import ModelSelect2MultipleWidget
from .models import Contact

class ParticipanteWidget(ModelSelect2MultipleWidget):
    model = Contact
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(owner=user)
        return qs.none()