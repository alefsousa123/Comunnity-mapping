from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from contact.models import GrupoFamilias, Contact, Familia, Rua
from contact.forms import GrupoFamiliasForm, GrupoPreJovensForm

@login_required(login_url="contact:login")
def family_group_list(request):
    grupos = GrupoFamilias.objects.filter(show=True, owner=request.user).order_by("-id")
    paginator = Paginator(grupos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "site_title": "Grupos de Famílias"
    }
    return render(request, "contact/family_group_page.html", context)

@login_required(login_url="contact:login")
def family_group_detail(request, pk):
    grupo = get_object_or_404(GrupoFamilias, pk=pk, show=True, owner=request.user)
    context = {
        "grupo": grupo,
        "site_title": f"Grupo: {grupo.nome}"
    }
    return render(request, "contact/family_group.html", context)

@login_required(login_url="contact:login")
def family_group_create(request):
    if request.method == "POST":
        form = GrupoFamiliasForm(request.POST, user=request.user)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.owner = request.user
            grupo.save()
            form.save_m2m()
            return redirect("contact:grupofamilias_detail", grupo.id)
    else:
        form = GrupoFamiliasForm(user=request.user)
    participantes = form.fields['participantes'].queryset
    familias = form.fields['familias'].queryset
    ruas = form.fields['ruas'].queryset
    context = {
        "form": form,
        "participantes": participantes,
        "familias": familias,
        "ruas": ruas,
        "site_title": "Criar Grupo de Famílias"
    }
    return render(request, "contact/partials/family_group-form.html", context)

@login_required(login_url="contact:login")
def family_group_update(request, pk):
    grupo = get_object_or_404(GrupoFamilias, pk=pk, show=True, owner=request.user)
    if request.method == "POST":
        post_data = request.POST.copy()
        # Mantém os antigos se nada for marcado
        if 'participantes' not in post_data or not post_data.getlist('participantes'):
            post_data.setlist('participantes', [str(pk) for pk in grupo.participantes.values_list('pk', flat=True)])
        if 'familias' not in post_data or not post_data.getlist('familias'):
            post_data.setlist('familias', [str(pk) for pk in grupo.familias.values_list('pk', flat=True)])
        if 'ruas' not in post_data or not post_data.getlist('ruas'):
            post_data.setlist('ruas', [str(pk) for pk in grupo.ruas.values_list('pk', flat=True)])
        form = GrupoFamiliasForm(post_data, instance=grupo, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("contact:grupofamilias_detail", grupo.id)
    else:
        form = GrupoFamiliasForm(instance=grupo, user=request.user)
    participantes = form.fields['participantes'].queryset
    familias = form.fields['familias'].queryset
    ruas = form.fields['ruas'].queryset
    context = {
        "form": form,
        "grupo": grupo,
        "participantes": participantes,
        "familias": familias,
        "ruas": ruas,
        "site_title": f"Editar Grupo: {grupo.nome}"
        
    }
    return render(request, "contact/partials/family_group-form.html", context)

@login_required(login_url="contact:login")
def family_group_delete(request, pk):
    grupo = get_object_or_404(GrupoFamilias, pk=pk, show=True, owner=request.user)
    confirmation = request.POST.get("confirmation", None)
    if request.method == "POST" and confirmation == "yes":
        grupo.delete()
        return redirect("contact:grupofamilias_list")
    context = {
        "grupo": grupo,
        "confirmation": confirmation,
        "site_title": f"Excluir Grupo: {grupo.nome}"
    }
    return render(request, "contact/family_group.html", context)

@login_required(login_url="contact:login")
def prejovens_group_create(request):
    if request.method == "POST":
        form = GrupoPreJovensForm(request.POST, user=request.user)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.owner = request.user
            grupo.save()
            form.save_m2m()
            return redirect("contact:grupoprejovens_detail", grupo.id)
    else:
        form = GrupoPreJovensForm(user=request.user)
    context = {
        'form': form,
        'prejovens': form.fields['pre_jovens'].queryset,
        'ruas': form.fields['rua'].queryset,
        'animadores': form.fields['animador'].queryset,
        "site_title": "Criar Grupo de Pré-Jovens"
    }
    return render(request, "contact/partials/prejovens_group-form.html", context)