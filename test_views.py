from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_form_view(request):
    if request.method == 'POST':
        html = "<h1>Dados POST Recebidos:</h1><ul>"
        for key, value in request.POST.items():
            if 'livro_' in key:
                html += f"<li><strong>{key}</strong>: '{value}'</li>"
        html += "</ul>"
        return HttpResponse(html)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste de Formulário - Django</title>
        <script>
            let contador = 0;
            
            function adicionarLivro(categoria) {
                contador++;
                const categoriaMap = {
                    'Sequência': 'sequencia',
                    'ABC': 'abc',
                    'Pré-jovens': 'prejovens',
                    'Outros': 'outros'
                };
                
                const categoriaBackend = categoriaMap[categoria];
                
                console.log(`Categoria: ${categoria} -> ${categoriaBackend}`);
                console.log(`Campo será: livro_${categoriaBackend}_${contador}_nome`);
                
                // Criar campo de teste
                const form = document.getElementById('testForm');
                const div = document.createElement('div');
                div.innerHTML = `
                    <input type="text" name="livro_${categoriaBackend}_${contador}_nome" 
                           value="Teste ${categoria}" placeholder="Nome do livro">
                    <input type="number" name="livro_${categoriaBackend}_${contador}_iniciados" 
                           value="1" placeholder="Iniciados">
                    <br>
                `;
                form.appendChild(div);
            }
        </script>
    </head>
    <body>
        <h1>Teste de Mapeamento de Categorias - Django</h1>
        
        <button onclick="adicionarLivro('Sequência')">Adicionar Sequência</button>
        <button onclick="adicionarLivro('ABC')">Adicionar ABC</button>
        <button onclick="adicionarLivro('Pré-jovens')">Adicionar Pré-jovens</button>
        <button onclick="adicionarLivro('Outros')">Adicionar Outros</button>
        
        <br><br>
        
        <form id="testForm" method="POST">
            <h3>Campos gerados:</h3>
            <br><br>
            <button type="submit">Enviar Teste</button>
        </form>
    </body>
    </html>
    """
    return HttpResponse(html)