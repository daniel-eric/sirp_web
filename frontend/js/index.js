document.addEventListener('DOMContentLoaded', function () {
    var filterIcon = document.querySelector('.search-input-container .filter-icon');
    var filterForm = document.getElementById('filter-form');

    if (filterIcon && filterForm) {
        filterIcon.addEventListener('click', function (e) {
            e.preventDefault();
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
