/**
 * Script para gerenciar seleção dinâmica de ciclos baseado no plano selecionado
 * Versão simplificada e mais robusta
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
    
    function updateOptions() {
        const planoId = planoField.value;
        console.log('Plano selecionado:', planoId);
        
        if (!planoId) {
            cicloField.innerHTML = '<option value="">Selecione um plano primeiro</option>';
            cicloField.disabled = true;
            return;
        }
        
        // Por enquanto, vamos usar uma lista estática de ciclos
        // Mais tarde implementaremos a consulta AJAX quando tudo estiver funcionando
        cicloField.innerHTML = '';
        cicloField.disabled = false;
        
        // Adicionar opção vazia
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = 'Usar ciclo atual';
        cicloField.appendChild(emptyOption);
        
        // Adicionar ciclos de 1 a 15 (será dinâmico depois)
        for (let i = 1; i <= 15; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Ciclo ${i}`;
            
            // Marcar ciclo 3 como atual (exemplo)
            if (i === 3) {
                option.textContent += ' (atual)';
                option.selected = true;
            } else if (i < 3) {
                option.textContent += ' (passado)';
            } else {
                option.textContent += ' (futuro)';
            }
            
            cicloField.appendChild(option);
        }
    }
    
    // Configurar evento de mudança
    planoField.addEventListener('change', updateOptions);
    
    // Inicializar
    updateOptions();
}

// Configurar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('Cycle selector carregado');
    
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
        }
    });
});