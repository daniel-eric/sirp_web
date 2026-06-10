document.addEventListener('DOMContentLoaded', function () {
    var container = document.querySelector('.profile-container');
    if (!container) return;

    container.addEventListener('click', function (e) {
        var btn = e.target.closest('.btn-edit-inline');
        if (btn) {
            var fieldId = btn.getAttribute('data-field-id');
            var input = document.getElementById(fieldId);
            if (input.disabled) {
                input.disabled = false;
                input.focus();
                btn.innerHTML = '&#10003;';
                btn.style.color = '#25d366';
            } else {
                btn.closest('form').submit();
            }
        }
    });

    container.addEventListener('submit', function (e) {
        var form = e.target;
        if (form.action && form.action.indexOf('/delete-account') !== -1) {
            if (!confirm('Tem certeza que deseja deletar sua conta? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        }
        if (form.action && form.action.indexOf('/desafios/delete') !== -1) {
            if (!confirm('Excluir este desafio? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        }
    });
});
