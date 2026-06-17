document.addEventListener('DOMContentLoaded', function () {
    var esqueceuSenha = document.getElementById('esqueceu-senha');
    if (esqueceuSenha) {
        esqueceuSenha.addEventListener('click', function (e) {
            e.preventDefault();
            var msg = document.getElementById('mensagem-sms');
            var username = document.getElementById('usernameInput').value.trim();

            if (!username) {
                msg.textContent = '📧 Digite seu email ou usuário primeiro!';
                msg.classList.add('visivel');
                setTimeout(function () { msg.classList.remove('visivel'); }, 4000);
                return;
            }

            msg.textContent = '📧 Enviando email...';
            msg.classList.add('visivel');

            fetch('/api/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ usernameInput: username })
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    msg.textContent = '📧 Email com a nova senha enviado!';
                } else {
                    msg.textContent = '⚠️ Não foi possível recuperar a senha.';
                }
                setTimeout(function () { msg.classList.remove('visivel'); }, 5000);
            })
            .catch(function () {
                msg.textContent = '⚠️ Erro de conexão. Tente novamente.';
                setTimeout(function () { msg.classList.remove('visivel'); }, 4000);
            });
        });
    }
});
