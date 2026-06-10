document.addEventListener('DOMContentLoaded', function () {
    var menuBtn = document.getElementById('menu');
    var menuNav = document.getElementById('menu-extensivel');
    if (menuBtn && menuNav) {
        menuBtn.addEventListener('click', function () {
            menuNav.classList.toggle('aberto');
        });
    }

    var btnOlho = document.getElementById('btn-olho');
    if (btnOlho) {
        var senhaInput = btnOlho.parentElement.querySelector('input[type="password"]');
        btnOlho.addEventListener('click', function () {
            senhaInput.type = senhaInput.type === 'password' ? 'text' : 'password';
        });
    }

    var logoutLink = document.getElementById('logout') || document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function (e) {
            e.preventDefault();
            fetch('/', {
                method: 'GET',
                credentials: 'same-origin'
            }).then(function () {
                window.location.href = '/';
            });
        });
    }
});
