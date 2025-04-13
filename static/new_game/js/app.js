/**
 * Main application script
 * Initializes the table and manages global events
 */
document.addEventListener('DOMContentLoaded', function() {
    // Create table rows
    const tableBody = document.getElementById('table-body');
    const rows = [];

    // Create 10 rows
    for (let i = 1; i <= 10; i++) {
        const tableRow = new TableRow(i);
        const rowElement = tableRow.render();
        tableBody.appendChild(rowElement);
        rows.push(tableRow);

        // Initialize row after it's added to the DOM
        tableRow.initialize();
    }

    // Handle global close dropdowns event
    document.addEventListener('closeAllDropdowns', function() {
        rows.forEach(row => row.closeDropdowns());
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        const isDropdownClick = event.target.closest('.dropdown');
        if (!isDropdownClick) {
            document.dispatchEvent(new CustomEvent('closeAllDropdowns'));
        }
    });
});