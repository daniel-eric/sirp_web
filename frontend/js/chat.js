document.addEventListener('DOMContentLoaded', function () {
    var conversaAtual = null;
    var ultimoId = 0;
    var pollingTimer = null;
    var loggedUser = document.body.dataset.loggedUser || '';

    var sidebarConvs = document.getElementById('sidebar-conversas');
    var chatEmpty = document.getElementById('chat-empty');
    var chatActive = document.getElementById('chat-active');
    var chatMessages = document.getElementById('chat-messages');
    var messagesPlaceholder = document.getElementById('messages-placeholder');
    var chatHeaderName = document.getElementById('chat-header-name');
    var chatHeaderMeta = document.getElementById('chat-header-meta');
    var inputMessage = document.getElementById('input-message');
    var btnSend = document.getElementById('btn-send');
    var btnNovoGrupo = document.getElementById('btn-novo-grupo');
    var btnNovaMsg = document.getElementById('btn-nova-msg');
    var btnBloquear = document.getElementById('btn-bloquear');
    var blockedBanner = document.getElementById('blocked-banner');
    var modalOverlay = document.getElementById('modal-overlay');
    var modalClose = document.getElementById('modal-close');
    var modalCancelar = document.getElementById('modal-cancelar');
    var modalCriar = document.getElementById('modal-criar');
    var modalError = document.getElementById('modal-error');

    var modalDmOverlay = document.getElementById('modal-dm-overlay');
    var modalDmClose = document.getElementById('modal-dm-close');
    var modalDmCancelar = document.getElementById('modal-dm-cancelar');
    var modalDmIniciar = document.getElementById('modal-dm-iniciar');
    var modalDmError = document.getElementById('modal-dm-error');
    var dmBusca = document.getElementById('dm-busca');
    var dmResultados = document.getElementById('dm-resultados');

    var IsBlocked = false;
    var BloqueadoPor = null;
    var conversasCache = {};

    function nomeOutroParticipante(conversa) {
        if (conversa.tipo !== 'dm') return conversa.nome;
        var participantes = conversa.participantes || [];
        for (var i = 0; i < participantes.length; i++) {
            if (participantes[i].user_email !== loggedUser) {
                return participantes[i].username || participantes[i].user_email;
            }
        }
        return conversa.nome;
    }

    carregarConversas();

    function carregarConversas() {
        fetch('/api/conversas')
            .then(function (res) {
                if (!res.ok) throw new Error('Erro ao carregar conversas');
                return res.json();
            })
            .then(function (data) {
                renderSidebar(data.conversas);
            })
            .catch(function (err) {
                console.error('Erro ao carregar conversas:', err);
            });
    }

    function renderSidebar(conversas) {
        sidebarConvs.innerHTML = '';
        if (conversas.length === 0) {
            sidebarConvs.innerHTML = '<div class="sidebar-placeholder">Nenhuma conversa ainda. Crie um grupo!</div>';
            return;
        }
        for (var i = 0; i < conversas.length; i++) {
            var c = conversas[i];
            conversasCache[c.id] = c;
            var div = document.createElement('div');
            div.className = 'sidebar-conversa';
            if (conversaAtual && conversaAtual === c.id) {
                div.classList.add('ativa');
            }
            div.dataset.id = c.id;

            var nome = c.tipo === 'dm' ? nomeOutroParticipante(c) : (c.nome || 'Sem nome');
            var info = c.tipo === 'dm' ? '' : (c.qtd_participantes ? c.qtd_participantes + ' membros' : '');

            div.innerHTML =
                '<div class="sidebar-conv-avatar">' + nome.charAt(0).toUpperCase() + '</div>' +
                '<div class="sidebar-conv-info">' +
                '  <span class="sidebar-conv-nome">' + escapeHtml(nome) + '</span>' +
                '  <span class="sidebar-conv-meta">' + info + '</span>' +
                '</div>';

            (function (id) {
                div.addEventListener('click', function () {
                    selecionarConversa(id);
                });
            })(c.id);

            sidebarConvs.appendChild(div);
        }
    }

    function selecionarConversa(id) {
        if (conversaAtual === id) return;

        conversaAtual = id;
        ultimoId = 0;
        chatMessages.innerHTML = '';
        if (messagesPlaceholder) messagesPlaceholder.style.display = '';

        var ativas = sidebarConvs.querySelectorAll('.sidebar-conversa.ativa');
        for (var i = 0; i < ativas.length; i++) {
            ativas[i].classList.remove('ativa');
        }
        var ativa = sidebarConvs.querySelector('.sidebar-conversa[data-id="' + id + '"]');
        if (ativa) ativa.classList.add('ativa');

        chatEmpty.style.display = 'none';
        chatActive.style.display = 'flex';

        var c = conversasCache[id];
        if (c) {
            if (c.tipo === 'dm') {
                chatHeaderName.textContent = nomeOutroParticipante(c);
                chatHeaderMeta.textContent = '';
            } else {
                chatHeaderName.textContent = c.nome;
                var participantes = c.participantes || [];
                var nomes = [];
                for (var i = 0; i < participantes.length; i++) {
                    nomes.push(participantes[i].username || participantes[i].user_email);
                }
                chatHeaderMeta.textContent = nomes.join(', ');
            }
        }

        pararPolling();
        carregarMensagens();
        iniciarPolling();
        verificarBloqueio();
    }

    function carregarMensagens() {
        if (!conversaAtual) return;

        fetch('/api/conversas/' + conversaAtual + '/mensagens?ultimo_id=' + ultimoId)
            .then(function (res) {
                if (!res.ok) throw new Error('Erro ao carregar mensagens');
                return res.json();
            })
            .then(function (data) {
                if (data.mensagens.length > 0) {
                    renderMensagens(data.mensagens);
                    ultimoId = data.mensagens[data.mensagens.length - 1].id;
                    if (messagesPlaceholder) messagesPlaceholder.style.display = 'none';
                }
            })
            .catch(function (err) {
                console.error('Erro ao carregar mensagens:', err);
            });
    }

    function renderMensagens(mensagens) {
        for (var i = 0; i < mensagens.length; i++) {
            var m = mensagens[i];
            var div = document.createElement('div');
            var isSent = m.autor_email === loggedUser;
            div.className = 'message ' + (isSent ? 'sent' : 'received');
            div.innerHTML =
                '<div class="message-text">' + escapeHtml(m.conteudo) + '</div>' +
                '<span class="message-time">' + formatarTempo(m.data_envio) + '</span>';
            chatMessages.appendChild(div);
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function iniciarPolling() {
        pararPolling();
        pollingTimer = setInterval(function () {
            carregarMensagens();
        }, 4000);
    }

    function pararPolling() {
        if (pollingTimer) {
            clearInterval(pollingTimer);
            pollingTimer = null;
        }
    }

    function enviarMensagem() {
        var conteudo = inputMessage.value.trim();
        if (!conteudo || !conversaAtual) return;

        fetch('/api/conversas/' + conversaAtual + '/mensagens', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conteudo: conteudo })
        })
            .then(function (res) {
                if (res.status === 423) {
                    console.warn('Conversa bloqueada');
                    verificarBloqueio();
                    return;
                }
                if (!res.ok) throw new Error('Erro ao enviar');
                return res.json();
            })
            .then(function () {
                inputMessage.value = '';
                carregarMensagens();
            })
            .catch(function (err) {
                console.error('Erro ao enviar mensagem:', err);
            });
    }

    function criarGrupo() {
        var nome = document.getElementById('grupo-nome').value.trim();
        var participantesRaw = document.getElementById('grupo-participantes').value.trim();
        modalError.textContent = '';

        if (!nome) {
            modalError.textContent = 'Informe um nome para o grupo.';
            return;
        }
        if (!participantesRaw) {
            modalError.textContent = 'Informe ao menos um participante.';
            return;
        }

        var participantes = [];
        var emails = participantesRaw.split(',');
        for (var i = 0; i < emails.length; i++) {
            var e = emails[i].trim();
            if (e) participantes.push(e);
        }

        if (participantes.length < 1) {
            modalError.textContent = 'Informe ao menos um participante.';
            return;
        }

        fetch('/api/conversas/criar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome, participantes: participantes })
        })
            .then(function (res) {
                if (!res.ok) return res.json().then(function (d) { throw new Error(d.erro || 'Erro ao criar'); });
                return res.json();
            })
            .then(function (data) {
                fecharModal();
                document.getElementById('grupo-nome').value = '';
                document.getElementById('grupo-participantes').value = '';
                carregarConversas();
                selecionarConversa(data.id);
            })
            .catch(function (err) {
                modalError.textContent = err.message;
            });
    }

    function abrirModal() {
        modalOverlay.style.display = 'flex';
        document.getElementById('grupo-nome').focus();
    }

    function fecharModal() {
        modalOverlay.style.display = 'none';
        modalError.textContent = '';
    }

    function formatarTempo(dataStr) {
        if (!dataStr) return '';
        var d = new Date(dataStr + 'Z');
        var h = d.getHours().toString().padStart(2, '0');
        var m = d.getMinutes().toString().padStart(2, '0');
        return h + ':' + m;
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    var dmSearchTimer = null;
    var dmUserSelecionado = null;

    function abrirModalDm() {
        dmUserSelecionado = null;
        dmBusca.value = '';
        dmResultados.innerHTML = '';
        modalDmError.textContent = '';
        modalDmIniciar.disabled = true;
        modalDmOverlay.style.display = 'flex';
        dmBusca.focus();
    }

    function fecharModalDm() {
        modalDmOverlay.style.display = 'none';
        dmBusca.value = '';
        dmResultados.innerHTML = '';
        modalDmError.textContent = '';
        modalDmIniciar.disabled = true;
        dmUserSelecionado = null;
    }

    function buscarUsuarios(termo) {
        if (!termo.trim()) {
            dmResultados.innerHTML = '';
            return;
        }
        fetch('/api/users/search?q=' + encodeURIComponent(termo))
            .then(function (res) {
                if (!res.ok) return [];
                return res.json();
            })
            .then(function (data) {
                var usuarios = data.users || [];
                dmResultados.innerHTML = '';
                if (usuarios.length === 0) {
                    dmResultados.innerHTML = '<div class="search-result-item search-result-empty">Nenhum usuário encontrado</div>';
                    return;
                }
                for (var i = 0; i < usuarios.length; i++) {
                    var u = usuarios[i];
                    var item = document.createElement('div');
                    item.className = 'search-result-item';
                    if (dmUserSelecionado && dmUserSelecionado.email === u.email) {
                        item.classList.add('selecionado');
                    }
                    item.innerHTML =
                        '<span class="search-result-nome">' + escapeHtml(u.username) + '</span>' +
                        '<span class="search-result-email">' + escapeHtml(u.email) + '</span>';
                    (function (user) {
                        item.addEventListener('click', function () {
                            var todos = dmResultados.querySelectorAll('.search-result-item');
                            for (var j = 0; j < todos.length; j++) {
                                todos[j].classList.remove('selecionado');
                            }
                            item.classList.add('selecionado');
                            dmUserSelecionado = user;
                            modalDmIniciar.disabled = false;
                            modalDmError.textContent = '';
                        });
                    })(u);
                    dmResultados.appendChild(item);
                }
            })
            .catch(function () {
                dmResultados.innerHTML = '<div class="search-result-item search-result-empty">Erro ao buscar</div>';
            });
    }

    if (dmBusca) {
        dmBusca.addEventListener('input', function () {
            clearTimeout(dmSearchTimer);
            var termo = dmBusca.value.trim();
            if (!termo) {
                dmResultados.innerHTML = '';
                return;
            }
            dmSearchTimer = setTimeout(function () {
                buscarUsuarios(termo);
            }, 300);
        });

        dmBusca.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (!modalDmIniciar.disabled) {
                    iniciarDm();
                }
            }
        });
    }

    function iniciarDm() {
        if (!dmUserSelecionado) {
            modalDmError.textContent = 'Selecione um usuário.';
            return;
        }

        fetch('/api/conversas/dm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: dmUserSelecionado.email })
        })
            .then(function (res) {
                if (!res.ok) return res.json().then(function (d) { throw new Error(d.erro || 'Erro ao criar DM'); });
                return res.json();
            })
            .then(function (data) {
                fecharModalDm();
                carregarConversas();
                selecionarConversa(data.id);
            })
            .catch(function (err) {
                modalDmError.textContent = err.message;
            });
    }

    function verificarBloqueio() {
        if (!conversaAtual) return;
        fetch('/api/conversas/' + conversaAtual + '/bloqueio')
            .then(function (res) { return res.json(); })
            .then(function (data) {
                IsBlocked = data.bloqueado;
                BloqueadoPor = data.bloqueado_por;
                if (IsBlocked) {
                    inputMessage.disabled = true;
                    btnSend.disabled = true;
                    if (blockedBanner) blockedBanner.style.display = 'block';
                    if (BloqueadoPor === loggedUser) {
                        // Eu bloqueei — posso desbloquear
                        btnBloquear.style.display = '';
                        btnBloquear.classList.add('blocked');
                        btnBloquear.querySelector('.lock-icon').className = 'fa-solid fa-lock lock-icon';
                        btnBloquear.querySelector('.lock-text').textContent = 'Desbloquear';
                        document.getElementById('blocked-banner-text').textContent =
                            'Você bloqueou esta conversa. Clique em Desbloquear para retomar.';
                    } else {
                        // Outro usuário bloqueou
                        btnBloquear.style.display = 'none';
                        document.getElementById('blocked-banner-text').textContent =
                            'Conversa bloqueada por ' + BloqueadoPor + '. Apenas esta pessoa pode desbloquear.';
                    }
                } else {
                    btnBloquear.style.display = '';
                    btnBloquear.classList.remove('blocked');
                    btnBloquear.querySelector('.lock-icon').className = 'fa-solid fa-lock-open lock-icon';
                    btnBloquear.querySelector('.lock-text').textContent = 'Bloquear';
                    inputMessage.disabled = false;
                    btnSend.disabled = false;
                    if (blockedBanner) blockedBanner.style.display = 'none';
                }
            })
            .catch(function () {
                btnBloquear.style.display = 'none';
            });
    }

    if (btnBloquear) {
        btnBloquear.addEventListener('click', function () {
            var action = IsBlocked ? 'desbloquear' : 'bloquear';
            fetch('/api/conversas/' + conversaAtual + '/' + action, { method: 'POST' })
                .then(function (res) {
                    if (!res.ok) throw new Error('Erro');
                    return res.json();
                })
                .then(function () {
                    verificarBloqueio();
                })
                .catch(function (err) {
                    console.error('Erro ao ' + action + ':', err);
                });
        });
    }

    btnSend.addEventListener('click', function (e) {
        e.preventDefault();
        enviarMensagem();
    });

    inputMessage.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            enviarMensagem();
        }
    });

    btnNovoGrupo.addEventListener('click', function () {
        abrirModal();
    });

    if (btnNovaMsg) {
        btnNovaMsg.addEventListener('click', function () {
            abrirModalDm();
        });
    }

    if (modalDmClose) modalDmClose.addEventListener('click', fecharModalDm);
    if (modalDmCancelar) modalDmCancelar.addEventListener('click', fecharModalDm);
    if (modalDmOverlay) {
        modalDmOverlay.addEventListener('click', function (e) {
            if (e.target === modalDmOverlay) fecharModalDm();
        });
    }
    if (modalDmIniciar) modalDmIniciar.addEventListener('click', iniciarDm);

    modalClose.addEventListener('click', fecharModal);
    modalCancelar.addEventListener('click', fecharModal);
    modalOverlay.addEventListener('click', function (e) {
        if (e.target === modalOverlay) fecharModal();
    });
    modalCriar.addEventListener('click', criarGrupo);
});
