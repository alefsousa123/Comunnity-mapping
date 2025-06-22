from django.shortcuts import render
from contact.forms import RegisterForm, RegisterUpdateForm
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required



def register(request):
    form = RegisterForm()

    messages.info(
        request,
        "Para registrar-se, preencha o formulário abaixo."
    )

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(
                request,
                "Registro realizado com sucesso! Você pode fazer login agora."
            )
            return redirect("contact:login")

    return render(
        request,
        "contact/register.html",
        context={"form": form, "site_title": "Registrar - ", "form_title": "Registrar"}
    )


def login_view(request):
    form = AuthenticationForm(request)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect("contact:index")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(
        request,
        "contact/login.html",
        {
            "form": form,
            "site_title": "Login - ",
            "form_title": "Entrar",
        }
    )

@login_required(login_url="contact:login")
def logout_view(request):
    auth.logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect("contact:login")

@login_required(login_url="contact:login")
def profile(request):
    form = RegisterUpdateForm(instance=request.user)

    if request.method != "POST":
        
        return render(
            request,
            "contact/register.html",
            {
                "form": form,
                "site_title": "Perfil - ",
                "form_title": "Atualizar Perfil",
            }
        )
    form = RegisterUpdateForm(data=request.POST, instance=request.user)
    if not form.is_valid():
        return render(
            request,
            "contact/register.html",
            {
                "form": form,
                "site_title": "Perfil - ",
                "form_title": "Atualizar Perfil",
            }
        )
    form.save()
    if form.cleaned_data.get('password1'):
        auth.logout(request)
        messages.success(request, "Senha alterada com sucesso! Faça login novamente.")
        return redirect("contact:login")
    messages.success(request, "Perfil atualizado com sucesso!")
    return redirect("contact:profile")