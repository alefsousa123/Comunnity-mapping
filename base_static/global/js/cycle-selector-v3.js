/**
 * Script para gerenciar seleção dinâmica de ciclos baseado no plano selecionado
 * Versão corrigida com fallback robusto
 */

// Função para atualizar ciclos baseado no plano selecionado
function updateCycleOptions(planoFieldId, cicloFieldId) {
    const planoField = document.getElementById(planoFieldId);
    const cicloField = document.getElementById(cicloFieldId);
    
    if (!planoField || !cicloField) {
        console.log('Campos não encontrados:', planoFieldId, cicloFieldId);
        return;
    }
    
    console.log('Configurando campos:', planoFieldId, cicloFieldId);
    
    function createStaticOptions(cicloAtual = 3, totalCiclos = 15) {
        // Criar opções estáticas como fallback
        cicloField.innerHTML = '';
        cicloField.disabled = false;
        
        // Adicionar opção vazia
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = 'Usar ciclo atual';
        cicloField.appendChild(emptyOption);
        
        // Adicionar ciclos de 1 até totalCiclos
        for (let i = 1; i <= totalCiclos; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Ciclo ${i}`;
            
            if (i === cicloAtual) {
                option.textContent += ' (atual)';
                option.selected = true;
            } else if (i < cicloAtual) {
                option.textContent += ' (passado)';
            } else {
                option.textContent += ' (futuro)';
            }
            
            cicloField.appendChild(option);
        }
    }
    
    function updateOptions() {
        const planoId = planoField.value;
        console.log('Plano selecionado:', planoId);
        
        if (!planoId) {
            cicloField.innerHTML = '<option value="">Selecione um plano primeiro</option>';
            cicloField.disabled = true;
            return;
        }
        
        console.log('Tentando carregar ciclos via AJAX...');
        
        // Tentar carregar via AJAX primeiro
        fetch(`/ciclos/plano/${planoId}/info/`)
            .then(response => {
                console.log('Response status:', response.status, 'OK:', response.ok);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Dados recebidos via AJAX:', data);
                
                if (!data.success || !data.plano) {
                    throw new Error('Dados inválidos recebidos do servidor');
                }
                
                cicloField.innerHTML = '';
                cicloField.disabled = false;
                
                // Adicionar opção vazia
                const emptyOption = document.createElement('option');
                emptyOption.value = '';
                emptyOption.textContent = 'Usar ciclo atual';
                cicloField.appendChild(emptyOption);
                
                // Adicionar ciclos dinâmicos
                const totalCiclos = data.plano.total_ciclos_plano || 15;
                const cicloAtual = data.plano.ciclo_atual || 3;
                
                for (let i = 1; i <= totalCiclos; i++) {
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = `Ciclo ${i}`;
                    
                    if (i === cicloAtual) {
                        option.textContent += ' (atual)';
                        option.selected = true;
                    } else if (i < cicloAtual) {
                        option.textContent += ' (passado)';
                    } else {
                        option.textContent += ' (futuro)';
                    }
                    
                    cicloField.appendChild(option);
                }
                
                console.log('Ciclos carregados com sucesso via AJAX');
            })
            .catch(error => {
                console.log('AJAX falhou, usando fallback estático. Erro:', error);
                createStaticOptions(); // Usar valores padrão
            });
    }
    
    // Configurar evento de mudança
    planoField.addEventListener('change', updateOptions);
    
    // Inicializar
    updateOptions();
}

// Configurar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cycle selector v3 carregado');
    
    // Verificar quais campos existem na página
    const formFields = [
        ['id_plano_ciclo', 'id_numero_ciclo_criacao'],    // Formulários padrão
        ['plano_id', 'ciclo_criacao']                      // Gerenciamento de estudos
    ];
    
    formFields.forEach(([planoId, cicloId]) => {
        const planoField = document.getElementById(planoId);
        const cicloField = document.getElementById(cicloId);
        
        if (planoField && cicloField) {
            console.log('Configurando campos encontrados:', planoId, cicloId);
            updateCycleOptions(planoId, cicloId);
        } else {
            console.log('Campos não encontrados:', planoId, cicloId);
        }
    });
});