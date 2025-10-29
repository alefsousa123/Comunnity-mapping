from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from contact.models import Livro, Contact, EstudoAtual, CategoriaLivro
from contact.forms import LivroForm, ContactForm, CategoriaLivroForm
from django.db.models import Q


@login_required
def livro_list(request):
    """Lista todos os livros organizados por categoria"""
    categorias = CategoriaLivro.objects.filter(ativo=True).prefetch_related(
        'livros__estudos_atuais__contato',
        'livros__historico_estudos__contato'
    ).order_by('ordem', 'nome')
    
    # Adicionar informações de estudos para cada livro do usuário atual
    for categoria in categorias:
        for livro in categoria.livros_ordenados:
            # Estudantes do usuário atual
            livro.meus_estudantes = Contact.objects.filter(
                estudos_atuais__livro=livro, 
                owner=request.user
            ).distinct()
            
            # Contadores
            livro.estudantes_ativos_count = livro.meus_estudantes.filter(estudos_atuais__status='em_andamento').count()
            livro.estudantes_concluidos_count = Contact.objects.filter(
                historico_estudos__livro=livro,
                historico_estudos__status='concluido',
                owner=request.user
            ).distinct().count()
    
    return render(request, 'contact/livro_list.html', {
        'categorias': categorias,
        'title': 'Livros e Materiais Educacionais'
    })


@login_required
def livro_detail(request, pk):
    """Visualizar detalhes de um livro e seus estudantes"""
    livro = get_object_or_404(Livro, pk=pk)
    
    # Estudantes deste livro pelo usuário atual
    meus_estudantes = Contact.objects.filter(
        livro_estudando=livro, 
        owner=request.user
    ).order_by('first_name')
    
    # Todos os estudantes atuais deste livro (do usuário)
    estudantes_atuais = Contact.objects.filter(
        livro_estudando=livro,
        status_estudo='em_andamento',
        owner=request.user
    ).order_by('first_name')
    
    # Estudantes que concluíram usando o histórico
    from django.db.models import Prefetch
    estudantes_concluidos = Contact.objects.filter(
        historico_estudos__livro=livro,
        historico_estudos__status='concluido',
        owner=request.user
    ).prefetch_related(
        Prefetch('historico_estudos', 
                queryset=livro.historico_estudos.filter(status='concluido'))
    ).distinct().order_by('first_name')
    
    return render(request, 'contact/livro_detail.html', {
        'livro': livro,
        'meus_estudantes': meus_estudantes,
        'estudantes_atuais': estudantes_atuais,
        'estudantes_concluidos': estudantes_concluidos,
        'title': str(livro)
    })


@login_required
def contato_estudos(request, contato_id):
    """Ver informações de estudo de um contato específico"""
    contato = get_object_or_404(Contact, pk=contato_id, owner=request.user)
    
    return render(request, 'contact/contato_estudos.html', {
        'contato': contato,
        'title': f'Estudos de {contato.first_name}'
    })


@login_required
def atribuir_livro(request, contato_id):
    """Atribuir ou alterar livro de estudo de um contato"""
    contato = get_object_or_404(Contact, pk=contato_id, owner=request.user)
    
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        status = request.POST.get('status', 'nao_iniciado')
        
        if livro_id:
            livro = get_object_or_404(Livro, pk=livro_id)
            contato.livro_estudando = livro
            contato.status_estudo = status
            
            if status == 'em_andamento':
                from datetime import date
                contato.data_inicio_estudo = date.today()
                contato.data_termino_estudo = None
            elif status == 'concluido':
                from datetime import date
                if not contato.data_inicio_estudo:
                    contato.data_inicio_estudo = date.today()
                contato.data_termino_estudo = date.today()
            
            contato.save()
            messages.success(request, f'Livro {livro} atribuído a {contato.first_name}')
        else:
            # Remover livro
            contato.livro_estudando = None
            contato.status_estudo = 'nao_iniciado'
            contato.data_inicio_estudo = None
            contato.data_termino_estudo = None
            contato.observacoes_estudo = ''
            contato.save()
            messages.success(request, f'Estudo removido de {contato.first_name}')
        
        return redirect('contact:contact', contact_id=contato.pk)
    
    livros = Livro.objects.filter(ativo=True).order_by('numero')
    
    return render(request, 'contact/atribuir_livro.html', {
        'contato': contato,
        'livros': livros,
        'title': f'Atribuir Livro - {contato.first_name}'
    })


@login_required
def quick_action_estudo(request, contato_id):
    """Ações rápidas no estudo: iniciar, pausar, concluir, retomar"""
    contato = get_object_or_404(Contact, pk=contato_id, owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'iniciar' and contato.livro_estudando:
            contato.iniciar_estudo(contato.livro_estudando)
            messages.success(request, f'Estudo iniciado para {contato.first_name}')
        elif action == 'pausar':
            contato.pausar_estudo()
            messages.success(request, f'Estudo pausado para {contato.first_name}')
        elif action == 'concluir':
            contato.concluir_estudo_e_adicionar_historico()
            messages.success(request, f'Estudo concluído para {contato.first_name}! Adicionado ao histórico.')
        elif action == 'retomar':
            contato.retomar_estudo()
            messages.success(request, f'Estudo retomado para {contato.first_name}')
    
    return redirect('contact:contact', contact_id=contato.pk)


@login_required
def livro_create(request):
    """Criar um novo livro"""
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            try:
                # Verificar se já existe um livro com esse número na mesma categoria
                numero = form.cleaned_data['numero']
                categoria = form.cleaned_data['categoria']
                if Livro.objects.filter(numero=numero, categoria=categoria).exists():
                    messages.error(request, f'Já existe um livro com o número {numero} na categoria {categoria}')
                else:
                    livro = form.save()
                    messages.success(request, f'Livro {livro.numero} - {livro.titulo} criado com sucesso!')
                    return redirect('contact:livro_list')
            except Exception as e:
                messages.error(request, f'Erro ao criar livro: {str(e)}')
    else:
        form = LivroForm()
    
    return render(request, 'contact/livro_create.html', {
        'form': form,
        'title': 'Novo Livro'
    })


@login_required
def livro_create_quick(request):
    """Criar um novo livro rapidamente (formulário inline)"""
    if request.method == 'POST':
        numero = request.POST.get('numero')
        titulo = request.POST.get('titulo', '')
        descricao = request.POST.get('descricao', '')
        ativo = request.POST.get('ativo') == 'on'
        categoria_id = request.POST.get('categoria')
        
        try:
            categoria = get_object_or_404(CategoriaLivro, pk=categoria_id)
            
            # Verificar se já existe um livro com esse número na mesma categoria
            if Livro.objects.filter(numero=numero, categoria=categoria).exists():
                messages.error(request, f'Já existe um livro com o número {numero} na categoria {categoria.nome}')
            else:
                livro = Livro.objects.create(
                    numero=numero,
                    titulo=titulo,
                    descricao=descricao,
                    ativo=ativo,
                    categoria=categoria
                )
                messages.success(request, f'Livro {livro.numero} criado com sucesso na categoria {categoria.nome}!')
        except Exception as e:
            messages.error(request, f'Erro ao criar livro: {str(e)}')
    
    return redirect('contact:livro_list')


@login_required
def livro_edit(request, pk):
    """Editar um livro"""
    livro = get_object_or_404(Livro, pk=pk)
    
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            try:
                # Verificar se já existe outro livro com esse número na mesma categoria
                numero = form.cleaned_data['numero']
                categoria = form.cleaned_data['categoria']
                if Livro.objects.filter(numero=numero, categoria=categoria).exclude(pk=pk).exists():
                    messages.error(request, f'Já existe outro livro com o número {numero} na categoria {categoria}')
                else:
                    livro = form.save()
                    messages.success(request, f'Livro {livro.numero} - {livro.titulo} atualizado com sucesso!')
                    return redirect('contact:livro_list')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar livro: {str(e)}')
    else:
        form = LivroForm(instance=livro)
    
    return render(request, 'contact/livro_edit.html', {
        'livro': livro,
        'form': form,
        'title': f'Editar {livro}'
    })


@login_required
def livro_delete(request, pk):
    """Excluir um livro do Instituto Ruhi"""
    livro = get_object_or_404(Livro, pk=pk)
    
    # Verificar se há contatos usando este livro
    contatos_usando = Contact.objects.filter(livro_estudando=livro).count()
    historicos_usando = livro.historico_estudos.count()
    estudos_atuais_usando = livro.estudos_atuais.count()
    
    if contatos_usando > 0 or historicos_usando > 0 or estudos_atuais_usando > 0:
        messages.error(request, f'Não é possível excluir o livro {livro}. Existem {contatos_usando} contatos estudando, {estudos_atuais_usando} estudos atuais e {historicos_usando} registros históricos.')
        return redirect('contact:livro_list')
    
    if request.method == 'POST':
        titulo = livro.titulo
        livro.delete()
        messages.success(request, f'Livro "{titulo}" excluído com sucesso!')
        return redirect('contact:livro_list')
    
    return render(request, 'contact/livro_delete.html', {
        'livro': livro,
        'title': f'Excluir {livro}'
    })


@login_required
def gerenciar_estudos(request, contato_id):
    """Gerenciar múltiplos estudos de um contato"""
    contato = get_object_or_404(Contact, pk=contato_id, owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar':
            livro_id = request.POST.get('livro_id')
            observacoes = request.POST.get('observacoes', '')
            plano_id = request.POST.get('plano_id')
            ciclo_criacao = request.POST.get('ciclo_criacao')
            
            if livro_id:
                livro = get_object_or_404(Livro, pk=livro_id)
                
                # Obter plano se especificado
                plano = None
                if plano_id:
                    from contact.models import ConfiguracaoEstatisticas
                    plano = get_object_or_404(ConfiguracaoEstatisticas, pk=plano_id, owner=request.user)
                
                # Converter ciclo para inteiro se especificado
                ciclo_int = None
                if ciclo_criacao:
                    try:
                        ciclo_int = int(ciclo_criacao)
                    except ValueError:
                        messages.error(request, 'Ciclo inválido')
                        return redirect('contact:gerenciar_estudos', contato_id=contato.pk)
                
                estudo, mensagem = contato.adicionar_estudo(
                    livro, 
                    observacoes=observacoes,
                    plano=plano,
                    ciclo_criacao=ciclo_int
                )
                
                if estudo:
                    messages.success(request, f'Livro {livro} adicionado aos estudos de {contato.first_name}')
                else:
                    messages.error(request, mensagem)
        
        elif action == 'remover':
            estudo_id = request.POST.get('estudo_id')
            
            try:
                estudo = EstudoAtual.objects.get(pk=estudo_id, contato=contato)
                livro_titulo = str(estudo.livro)
                estudo.delete()
                messages.success(request, f'Estudo "{livro_titulo}" removido com sucesso')
            except EstudoAtual.DoesNotExist:
                messages.error(request, 'Estudo não encontrado')
        
        elif action == 'concluir':
            estudo_id = request.POST.get('estudo_id')
            observacoes_conclusao = request.POST.get('observacoes_conclusao', '')
            
            try:
                estudo = EstudoAtual.objects.get(pk=estudo_id, contato=contato)
                livro_titulo = str(estudo.livro)
                estudo.concluir(observacoes_conclusao)
                messages.success(request, f'Estudo "{livro_titulo}" concluído e adicionado ao histórico!')
            except EstudoAtual.DoesNotExist:
                messages.error(request, 'Estudo não encontrado')
        
        elif action == 'pausar':
            estudo_id = request.POST.get('estudo_id')
            
            try:
                estudo = EstudoAtual.objects.get(pk=estudo_id, contato=contato)
                estudo.pausar()
                messages.success(request, f'Estudo "{estudo.livro}" pausado')
            except EstudoAtual.DoesNotExist:
                messages.error(request, 'Estudo não encontrado')
        
        elif action == 'retomar':
            estudo_id = request.POST.get('estudo_id')
            
            try:
                estudo = EstudoAtual.objects.get(pk=estudo_id, contato=contato)
                estudo.retomar()
                messages.success(request, f'Estudo "{estudo.livro}" retomado')
            except EstudoAtual.DoesNotExist:
                messages.error(request, 'Estudo não encontrado')
        
        return redirect('contact:gerenciar_estudos', contato_id=contato.pk)
    
    # Filtro por categoria
    categoria_selecionada = request.GET.get('categoria')
    
    # Livros disponíveis para adicionar
    livros_ja_estudando = contato.estudos_atuais.values_list('livro_id', flat=True)
    livros_ja_concluidos = contato.historico_estudos.filter(status='concluido').values_list('livro_id', flat=True)
    
    livros_query = Livro.objects.filter(ativo=True).exclude(
        id__in=list(livros_ja_estudando) + list(livros_ja_concluidos)
    )
    
    # Aplicar filtro de categoria se selecionada
    if categoria_selecionada and categoria_selecionada != 'todos':
        livros_query = livros_query.filter(categoria_id=categoria_selecionada)
    
    livros_disponiveis = livros_query.order_by('numero')
    
    # Categorias disponíveis
    categorias = CategoriaLivro.objects.filter(ativo=True).order_by('ordem', 'nome')
    
    # Planos de ciclos disponíveis
    from contact.models import ConfiguracaoEstatisticas
    planos_disponiveis = ConfiguracaoEstatisticas.objects.filter(
        owner=request.user, ativo=True
    ).order_by('-principal', 'titulo_plano')
    
    return render(request, 'contact/gerenciar_estudos.html', {
        'contato': contato,
        'livros_disponiveis': livros_disponiveis,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'planos_disponiveis': planos_disponiveis,
        'title': f'Gerenciar Estudos - {contato.first_name}'
    })


@login_required
def categoria_list(request):
    """Redireciona para a página de livros onde as categorias podem ser gerenciadas"""
    return redirect('contact:livro_list')


@login_required
def categoria_create(request):
    """Criar uma nova categoria de livros"""
    if request.method == 'POST':
        form = CategoriaLivroForm(request.POST)
        if form.is_valid():
            try:
                categoria = form.save()
                messages.success(request, f'Categoria "{categoria.nome}" criada com sucesso!')
                return redirect('contact:livro_list')
            except Exception as e:
                messages.error(request, f'Erro ao criar categoria: {str(e)}')
    else:
        form = CategoriaLivroForm()
    
    return render(request, 'contact/categoria_create.html', {
        'form': form,
        'title': 'Criar Nova Categoria'
    })


@login_required
def categoria_edit(request, pk):
    """Editar uma categoria de livros"""
    categoria = get_object_or_404(CategoriaLivro, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaLivroForm(request.POST, instance=categoria)
        if form.is_valid():
            try:
                categoria = form.save()
                messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
                return redirect('contact:livro_list')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar categoria: {str(e)}')
    else:
        form = CategoriaLivroForm(instance=categoria)
    
    return render(request, 'contact/categoria_edit.html', {
        'categoria': categoria,
        'form': form,
        'title': f'Editar Categoria - {categoria.nome}'
    })


@login_required
def categoria_delete(request, pk):
    """Excluir uma categoria de livros"""
    categoria = get_object_or_404(CategoriaLivro, pk=pk)
    
    # Verificar se há livros nesta categoria
    total_livros = categoria.livros.count()
    
    if total_livros > 0:
        messages.error(request, f'Não é possível excluir a categoria "{categoria.nome}". Existem {total_livros} livros associados.')
        return redirect('contact:livro_list')
    
    if request.method == 'POST':
        nome = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
        return redirect('contact:livro_list')
    
    return render(request, 'contact/categoria_delete.html', {
        'categoria': categoria,
        'title': f'Excluir Categoria - {categoria.nome}'
    })