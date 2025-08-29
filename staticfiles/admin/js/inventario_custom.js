document.addEventListener('DOMContentLoaded', function () {
    function toggleMemoriaInput() {
        const memoriaSelect = document.querySelector('#id_memoria_select');
        const memoriaInput = document.querySelector('#id_memoria')?.closest('.form-row');

        if (memoriaSelect && memoriaInput) {
            memoriaInput.style.display = (memoriaSelect.value === 'outros') ? '' : 'none';
        }
    }

    function toggleIpInput() {
        const tipoIpSelect = document.querySelector('#id_tipo_ip_select');
        const ipInput = document.querySelector('#id_numero_ip')?.closest('.form-row');

        if (tipoIpSelect && ipInput) {
            ipInput.style.display = (tipoIpSelect.value === 'fixo') ? '' : 'none';
        }
    }
    
    function toggleAtribuidoInput() {
        const atribuidoCheck = document.querySelector('#id_atribuido_check');
        const atribuidoField = document.querySelector('#id_atribuido')?.closest('.form-row');

        if (atribuidoCheck && atribuidoField) {
            atribuidoField.style.display = atribuidoCheck.checked ? '' : 'none';
            document.querySelector('#id_atribuido').disabled = !atribuidoCheck.checked;
        }
    }

    function preencherGarantia() {
        const dataCompraInput = document.querySelector('#id_data_compra');
        const dataGarantiaInput = document.querySelector('#id_data_garantia');

        function adicionarDoisAnos(data) {
            const novaData = new Date(data);
            novaData.setFullYear(novaData.getFullYear() + 2);
            return novaData.toISOString().split('T')[0];
        }

        if (dataCompraInput && dataGarantiaInput) {
            dataCompraInput.addEventListener('change', function () {
                if (!dataGarantiaInput.value) {
                    const dataCompra = this.value;
                    if (dataCompra) {
                        dataGarantiaInput.value = adicionarDoisAnos(dataCompra);
                    }
                }
            });
        }
    }

    toggleMemoriaInput();
    toggleIpInput();
    toggleAtribuidoInput();
    preencherGarantia();

    document.querySelector('#id_memoria_select')?.addEventListener('change', toggleMemoriaInput);
    document.querySelector('#id_tipo_ip_select')?.addEventListener('change', toggleIpInput);
    document.querySelector('#id_atribuido_check')?.addEventListener('change', toggleAtribuidoInput);
});
