document.addEventListener('DOMContentLoaded', function () {
    var chatAtivo = false;
    var chatFinalizado = false;

    function adicionarMsg(tipo, texto) {
        var container = document.getElementById('chat-messages');
        var div = document.createElement('div');
        div.className = 'msg ' + (tipo === 'bot' ? 'msg-bot' : 'msg-user');
        div.textContent = texto;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function setCarregando(ativo) {
        document.getElementById('chat-input').disabled = ativo;
        document.getElementById('chat-send').disabled = ativo;
        document.getElementById('chat-status').textContent = ativo ? 'Processando...' : '';
    }

    function setInputHabilitado(habilitado) {
        document.getElementById('chat-input').disabled = !habilitado;
        document.getElementById('chat-send').disabled = !habilitado;
        if (habilitado) document.getElementById('chat-input').focus();
    }

    async function iniciarChat() {
        document.getElementById('btn-iniciar-chat').style.display = 'none';
        document.getElementById('chat-container').classList.add('ativo');
        chatAtivo = true;

        setCarregando(true);
        try {
            var resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem: 'iniciar' })
            });
            var data = await resp.json();
            if (data.resposta) {
                adicionarMsg('bot', data.resposta);
            }
            setInputHabilitado(true);
        } catch (e) {
            adicionarMsg('bot', 'Erro ao conectar com o assistente. Tente novamente.');
        }
        setCarregando(false);
    }

    async function enviarMensagem() {
        if (!chatAtivo || chatFinalizado) return;

        var input = document.getElementById('chat-input');
        var msg = input.value.trim();
        if (!msg) return;

        adicionarMsg('user', msg);
        input.value = '';
        setCarregando(true);

        try {
            var resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensagem: msg })
            });
            var data = await resp.json();

            if (data.resposta) {
                adicionarMsg('bot', data.resposta);
            }

            if (data.rascunho_pronto && !data.finalizado) {
                setInputHabilitado(true);
                document.getElementById('chat-status').textContent =
                    'Revise o rascunho acima e digite "perfeito" para publicar, ou peça ajustes.';
            }

            if (data.finalizado) {
                chatFinalizado = true;
                setInputHabilitado(false);

                if (data.rascunho) {
                    var r = data.rascunho;
                    if (r['Título']) document.getElementById('titulo').value = r['Título'];
                    if (r['Áreas']) document.getElementById('areas').value = r['Áreas'];
                    if (r['Contexto']) document.getElementById('contexto').value = r['Contexto'];
                    if (r['Atores']) document.getElementById('atores').value = r['Atores'];
                    if (r['Impacto']) document.getElementById('impacto').value = r['Impacto'];
                    if (r['Contornos']) document.getElementById('contornos').value = r['Contornos'];
                    if (r['Métricas de Sucesso']) document.getElementById('metricas_sucesso').value = r['Métricas de Sucesso'];
                    if (r['Restrições']) document.getElementById('restricoes').value = r['Restrições'];

                    adicionarMsg('bot', 'Desafio salvo! Os campos foram preenchidos no formulário.');
                }

                document.getElementById('chat-status').textContent = 'Assistente finalizado. Desafio registrado!';
            }
        } catch (e) {
            adicionarMsg('bot', 'Erro de conexão. Tente novamente.');
        }
        setCarregando(false);
    }

    document.getElementById('chat-send').addEventListener('click', enviarMensagem);
    document.getElementById('chat-input').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') enviarMensagem();
    });

    var btnIniciar = document.getElementById('btn-iniciar-chat');
    if (btnIniciar) {
        btnIniciar.addEventListener('click', iniciarChat);
    }
});
