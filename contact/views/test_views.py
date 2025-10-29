from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def teste_ciclos_view(request):
    """View de teste para verificar funcionamento da seleção de ciclos"""
    return render(request, 'global/teste_ciclos.html')