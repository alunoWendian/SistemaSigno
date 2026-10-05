document.getElementById('formSigno').addEventListener('submit', async function (e) {
    e.preventDefault();

    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const dataNascimento = document.getElementById('data_nascimento').value;

    const mensagemErro = document.getElementById('mensagemErro');
    const resultadoContainer = document.getElementById('resultadoContainer');
    const listaCaracteristicas = document.getElementById('listaCaracteristicas');

    // Limpa estados e exibições anteriores
    mensagemErro.classList.add('escondido');
    resultadoContainer.classList.add('escondido');
    listaCaracteristicas.innerHTML = '';

    try {
        const resposta = await fetch('/api/descobrir-signo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nome: nome,
                email: email,
                data_nascimento: dataNascimento
            })
        });

        const dados = await resposta.json();

        if (dados.sucesso) {
            // Preenche dados básicos do signo
            document.getElementById('resNome').textContent = dados.usuario;
            document.getElementById('resSigno').textContent = dados.signo.nome;
            document.getElementById('resElemento').textContent = dados.signo.elemento;
            document.getElementById('resPlaneta').textContent = dados.signo.planeta;

            // Preenche a lista de características trazida do banco
            if (dados.signo.caracteristicas && dados.signo.caracteristicas.length > 0) {
                dados.signo.caracteristicas.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${item.tipo || 'Característica'}:</strong> ${item.descricao}`;
                    listaCaracteristicas.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'Nenhuma característica cadastrada para este signo.';
                listaCaracteristicas.appendChild(li);
            }

            resultadoContainer.classList.remove('escondido');
        } else {
            mensagemErro.textContent = dados.mensagem;
            mensagemErro.classList.remove('escondido');
        }
    } catch (erro) {
        mensagemErro.textContent = "Erro ao conectar com o servidor. Tente novamente mais tarde.";
        mensagemErro.classList.remove('escondido');
    }
});