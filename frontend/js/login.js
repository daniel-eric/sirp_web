document.addEventListener('DOMContentLoaded', function () {
    var esqueceuSenha = document.getElementById('esqueceu-senha');
    if (esqueceuSenha) {
        esqueceuSenha.addEventListener('click', function (e) {
            e.preventDefault();
            var msg = document.getElementById('mensagem-sms');
            msg.classList.add('visivel');
            setTimeout(function () {
                msg.classList.remove('visivel');
            }, 4000);
        });
    }
});
