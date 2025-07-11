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

    toggleMemoriaInput();
    toggleIpInput();

    document.querySelector('#id_memoria_select')?.addEventListener('change', toggleMemoriaInput);
    document.querySelector('#id_tipo_ip_select')?.addEventListener('change', toggleIpInput);
});
