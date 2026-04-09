// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Gestion des alertes auto-fermantes
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Animation au scroll pour les éléments avec la classe .fade-in-scroll
    function handleScrollAnimation() {
        var elements = document.querySelectorAll('.fade-in-scroll');
        elements.forEach(function(element) {
            var position = element.getBoundingClientRect();
            if(position.top < window.innerHeight) {
                element.classList.add('visible');
            }
        });
    }

    window.addEventListener('scroll', handleScrollAnimation);
    handleScrollAnimation();

    // Gestion des formulaires de confirmation
    var confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Gestion des liens de suppression
    var deleteLinks = document.querySelectorAll('a[data-delete]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var message = this.getAttribute('data-delete');
            if (confirm(message)) {
                window.location.href = this.href;
            }
        });
    });

    // Gestion des tables triables
    var sortableTables = document.querySelectorAll('table.sortable');
    sortableTables.forEach(function(table) {
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.addEventListener('click', function() {
                var column = this.cellIndex;
                var rows = Array.from(table.querySelectorAll('tbody tr'));
                var isAsc = this.classList.contains('asc');
                
                rows.sort(function(a, b) {
                    var aVal = a.cells[column].textContent;
                    var bVal = b.cells[column].textContent;
                    
                    if (isNaN(aVal)) {
                        return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
                    } else {
                        return isAsc ? bVal - aVal : aVal - bVal;
                    }
                });

                headers.forEach(h => h.classList.remove('asc', 'desc'));
                this.classList.toggle('asc', !isAsc);
                this.classList.toggle('desc', isAsc);

                var tbody = table.querySelector('tbody');
                rows.forEach(function(row) {
                    tbody.appendChild(row);
                });
            });
        });
    });

    // Gestion de la recherche dans les tables
    var tableSearchInputs = document.querySelectorAll('.table-search');
    tableSearchInputs.forEach(function(input) {
        input.addEventListener('keyup', function() {
            var searchValue = this.value.toLowerCase();
            var tableId = this.getAttribute('data-table');
            var table = document.getElementById(tableId);
            var rows = table.querySelectorAll('tbody tr');

            rows.forEach(function(row) {
                var text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchValue) ? '' : 'none';
            });
        });
    });

    // Gestion des formulaires AJAX
    var ajaxForms = document.querySelectorAll('form[data-ajax]');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var formData = new FormData(this);
            var url = this.action;
            var method = this.method;

            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                    if (data.message) {
                        showNotification(data.message, 'success');
                    }
                } else {
                    showNotification(data.message || 'Une erreur est survenue', 'error');
                }
            })
            .catch(error => {
                showNotification('Une erreur est survenue', 'error');
            });
        });
    });

    // Fonction pour afficher les notifications
    function showNotification(message, type = 'info') {
        var notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, 5000);
    }
}); 