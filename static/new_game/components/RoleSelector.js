/**
 * Role Selector Component
 * Handles the role selection functionality for a table row
 */
class RoleSelector {
    /**
     * Creates a role selector component
     * @param {number} rowId - The ID of the row this selector belongs to
     * @param {string} initialRole - The initial role for this selector
     * @param {Function} onRoleChange - Callback when role changes
     */
    constructor(rowId, initialRole, onRoleChange) {
        this.rowId = rowId;
        this.role = initialRole || 'user';
        this.onRoleChange = onRoleChange;
        this.dropdownId = `role-dropdown-${rowId}`;
        this.iconId = `role-icon-${rowId}`;
        this.optionsId = `role-options-${rowId}`;
    }

    /**
     * Renders the role selector component
     * @returns {string} The HTML for the role selector
     */
    render() {
        return `
            <div class="dropdown" id="${this.dropdownId}">
                <div class="role-icon" id="${this.iconId}">
                    ${ROLES[this.role].label}
                </div>
                <div class="dropdown-content" id="${this.optionsId}" style="display: none;">
                    <!-- Role options will be added by JavaScript -->
                </div>
            </div>
        `;
    }

    /**
     * Initializes the component after it's been rendered to the DOM
     */
    initialize() {
        const roleIcon = document.getElementById(this.iconId);
        const roleOptions = document.getElementById(this.optionsId);

        // Set initial role icon
        roleIcon.style.backgroundColor = ROLES[this.role].color;
        roleIcon.textContent = ROLES[this.role].label;

        // Add role options
        Object.entries(ROLES).forEach(([role, data]) => {
            const option = document.createElement('div');
            option.className = 'role-icon';
            option.style.backgroundColor = data.color;
            option.textContent = data.label;
            option.addEventListener('click', () => {
                // Update role
                this.role = role;
                roleIcon.style.backgroundColor = data.color;
                roleIcon.textContent = data.label;
                roleOptions.style.display = 'none';

                // Notify parent component
                if (this.onRoleChange) {
                    this.onRoleChange(role);
                }
            });
            roleOptions.appendChild(option);
        });

        // Add role dropdown toggle
        roleIcon.addEventListener('click', (event) => {
            event.stopPropagation();
            const isVisible = roleOptions.style.display === 'block';

            // Close all dropdowns first
            document.dispatchEvent(new CustomEvent('closeAllDropdowns'));

            // Then open this one if it was closed
            if (!isVisible) {
                roleOptions.style.display = 'block';
            }
        });
    }

    /**
     * Closes the dropdown menu if it's open
     */
    closeDropdown() {
        const roleOptions = document.getElementById(this.optionsId);
        if (roleOptions) {
            roleOptions.style.display = 'none';
        }
    }
}