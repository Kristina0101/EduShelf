document.addEventListener('DOMContentLoaded', function() {
    // Функция для адаптации таблицы
    function adaptTable() {
        const table = document.querySelector('.table');
        if (!table) return;
        
        const headers = table.querySelectorAll('thead th');
        const rows = table.querySelectorAll('tbody tr');
        
        // Добавляем data-label для всех ячеек
        headers.forEach((header, index) => {
            const label = header.textContent.trim();
            rows.forEach(row => {
                const cell = row.cells[index];
                if (cell) {
                    cell.setAttribute('data-label', label);
                }
            });
        });
        
        // Адаптация для мобильных устройств
        if (window.innerWidth <= 768) {
            table.classList.add('mobile-table');
        } else {
            table.classList.remove('mobile-table');
        }
    }
    
    // Инициализация при загрузке
    adaptTable();
    
    // Адаптация при изменении размера
    window.addEventListener('resize', adaptTable);
    
    // Мобильное меню
    function initMobileMenu() {
        const nav = document.querySelector('nav');
        if (!nav) return;
        
        const menuBtn = document.querySelector('.mobile-menu-btn') || document.createElement('button');
        menuBtn.className = 'mobile-menu-btn';
        menuBtn.innerHTML = '☰ Меню';
        
        const navUl = nav.querySelector('ul');
        
        function toggleMenu() {
            navUl.style.display = navUl.style.display === 'none' ? 'flex' : 'none';
        }
        
        menuBtn.onclick = toggleMenu;
        
        if (window.innerWidth <= 992) {
            if (!document.querySelector('.mobile-menu-btn')) {
                nav.insertBefore(menuBtn, navUl);
            }
            navUl.style.display = 'none';
        } else {
            if (document.querySelector('.mobile-menu-btn')) {
                nav.removeChild(menuBtn);
            }
            navUl.style.display = 'flex';
        }
    }
    
    initMobileMenu();
    window.addEventListener('resize', initMobileMenu);
});