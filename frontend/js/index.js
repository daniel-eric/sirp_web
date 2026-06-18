document.addEventListener('DOMContentLoaded', function () {
    var filterIcon = document.querySelector('.search-input-container .filter-icon');
    var filterForm = document.getElementById('filter-form');
    var searchInput = document.getElementById('search-input');
    var modeToggle = document.querySelector('.search-mode-toggle');
    var userResults = document.getElementById('user-results');
    var currentMode = 'problems';
    var debounceTimer = null;

    function setMode(mode) {
        currentMode = mode;
        var btns = modeToggle.querySelectorAll('.search-mode-btn');
        for (var i = 0; i < btns.length; i++) {
            btns[i].classList.toggle('ativo', btns[i].dataset.mode === mode);
        }

        var folders = document.querySelectorAll('.folder');
        var emptyFeed = document.querySelector('.empty-feed');

        if (mode === 'users') {
            searchInput.placeholder = 'Buscar usuários por nome ou email...';
            searchInput.name = '';
            userResults.style.display = 'block';
            for (var i = 0; i < folders.length; i++) {
                folders[i].style.display = 'none';
            }
            if (emptyFeed) emptyFeed.style.display = 'none';
        } else {
            searchInput.placeholder = 'Buscar problemas...';
            searchInput.name = 'title';
            userResults.style.display = 'none';
            userResults.innerHTML = '';
            for (var i = 0; i < folders.length; i++) {
                folders[i].style.display = '';
            }
            if (emptyFeed) emptyFeed.style.display = '';
        }
    }

    modeToggle.addEventListener('click', function (e) {
        var btn = e.target.closest('.search-mode-btn');
        if (!btn) return;
        setMode(btn.dataset.mode);
        if (currentMode === 'users' && searchInput.value.trim()) {
            searchUsers(searchInput.value.trim());
        }
    });

    function renderUsers(users) {
        userResults.innerHTML = '';
        if (users.length === 0) {
            userResults.innerHTML = '<div class="empty-feed"><p class="empty-feed-text">Nenhum usuário encontrado.</p></div>';
            return;
        }
        for (var i = 0; i < users.length; i++) {
            var user = users[i];
            var card = document.createElement('div');
            card.className = 'user-card';

            var avatar = document.createElement('div');
            avatar.className = 'user-card-avatar';
            avatar.textContent = user.username.charAt(0).toUpperCase();

            var info = document.createElement('div');
            info.className = 'user-card-info';

            var name = document.createElement('span');
            name.className = 'user-card-name';
            name.textContent = user.username;

            var email = document.createElement('span');
            email.className = 'user-card-email';
            email.textContent = user.email;

            info.appendChild(name);
            info.appendChild(email);
            card.appendChild(avatar);
            card.appendChild(info);

            if (user.tellNum) {
                var phone = document.createElement('span');
                phone.className = 'user-card-phone';
                phone.textContent = user.tellNum;
                card.appendChild(phone);
            }

            userResults.appendChild(card);
        }
    }

    function searchUsers(query) {
        if (!query.trim()) {
            userResults.innerHTML = '';
            return;
        }
        fetch('/api/users/search?q=' + encodeURIComponent(query.trim()))
            .then(function (res) {
                if (!res.ok) throw new Error('Erro na busca');
                return res.json();
            })
            .then(function (data) {
                renderUsers(data.users);
            })
            .catch(function (err) {
                userResults.innerHTML = '<div class="empty-feed"><p class="empty-feed-text">Erro ao buscar usuários.</p></div>';
            });
    }

    function handleInput() {
        if (currentMode === 'users') {
            if (debounceTimer) clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                searchUsers(searchInput.value);
            }, 300);
        }
    }

    searchInput.addEventListener('input', handleInput);

    var searchWrapper = document.querySelector('.search-wrapper');
    if (searchWrapper) {
        searchWrapper.addEventListener('submit', function (e) {
            if (currentMode === 'users') {
                e.preventDefault();
                searchUsers(searchInput.value);
            }
        });
    }

    if (filterIcon && filterForm) {
        filterIcon.addEventListener('click', function (e) {
            e.preventDefault();
            if (currentMode === 'users') {
                searchUsers(searchInput.value);
                return;
            }
            var filters = document.getElementById('advanced-filters');
            if (!filters.classList.contains('visivel')) {
                filters.classList.add('visivel');
            } else {
                filterForm.submit();
            }
        });
    }

    document.querySelector('.feed-section').addEventListener('click', function (e) {
        var folder = e.target.closest('.folder');
        if (folder) {
            folder.classList.toggle('aberta');
        }
    });
});
