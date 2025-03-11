// Общие функции
function toggleLoader(show) {
    document.querySelector('.loading-overlay').style.display = show ? 'flex' : 'none';
}

// Прогресс бар скролла
function initScrollProgress() {
    window.addEventListener('scroll', () => {
        const progress = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        document.getElementById('progress-bar').style.width = `${progress}%`;
    });
}

// Сортировка таблицы
function initTableSorting() {
    document.querySelectorAll('th[data-column]').forEach(header => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = header.dataset.column;
            
            rows.sort((a, b) => {
                const aValue = a.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent;
                const bValue = b.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent;
                return isNaN(aValue) ? aValue.localeCompare(bValue) : aValue - bValue;
            });

            tbody.style.transition = 'opacity 0.3s ease';
            tbody.style.opacity = '0.4';
            
            setTimeout(() => {
                rows.forEach(row => tbody.appendChild(row));
                tbody.style.opacity = '1';
            }, 300);
        });
    });
}


// Анимации
function animateElement(element, animation, duration = 300) {
    element.style.animation = `${animation} ${duration}ms ease-out`;
    setTimeout(() => element.style.animation = '', duration);
}

function animateShake(element) {
    element.style.transform = 'translateX(5px)';
    setTimeout(() => {
        element.style.transform = 'translateX(-5px)';
        setTimeout(() => element.style.transform = '', 100);
    }, 100);
}

function animatePulse(element) {
    element.style.transform = 'scale(1.05)';
    setTimeout(() => element.style.transform = '', 200);
}

// Уведомления
function showErrorMessage(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.classList.add('visible');
    setTimeout(() => errorEl.classList.remove('visible'), 3000);
}

function showSuccessMessage(message) {
    const successEl = document.createElement('div');
    successEl.className = 'success-message';
    successEl.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
    `;
    document.body.appendChild(successEl);
    setTimeout(() => successEl.remove(), 2000);
}

// Эффекты ввода
function initInputEffects() {
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });
}

// Инициализация чекбоксов
function initCheckboxes() {
    document.querySelectorAll('.pu-checkbox input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            this.parentElement.classList.toggle('checked', this.checked);
        });
    });
}