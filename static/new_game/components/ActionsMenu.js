/**
 * Actions Menu Component
 * Handles the actions menu functionality for a table row
 */
class ActionsMenu {
    /**
     * Creates an actions menu component
     * @param {number} rowId - The ID of the row this menu belongs to
     * @param {Array} initialActions - The initial actions configuration
     * @param {Function} onActionToggle - Callback when an action is toggled
     */
    constructor(rowId, initialActions, onActionToggle) {
        this.rowId = rowId;
        this.actions = initialActions.map(action => ({
            ...action,
            active: false
        }));
        this.onActionToggle = onActionToggle;
        this.dropdownId = `actions-dropdown-${rowId}`;
        this.toggleId = `actions-toggle-${rowId}`;
        this.menuId = `actions-menu-${rowId}`;
        this.iconsContainerId = `action-icons-${rowId}`;
    }

    /**
     * Renders the actions menu component
     * @returns {string} The HTML for the actions menu
     */
    render() {
        return `
            <div class="dropdown" id="${this.dropdownId}">
                <div class="three-dots" id="${this.toggleId}">⋮</div>
                <div class="dropdown-content" id="${this.menuId}" style="display: none;">
                    <div class="icon-selector" id="${this.iconsContainerId}">
                        <!-- Action icons will be added by JavaScript -->
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Initializes the component after it's been rendered to the DOM
     */
    initialize() {
        const actionsToggle = document.getElementById(this.toggleId);
        const actionsMenu = document.getElementById(this.menuId);
        const actionIconsContainer = document.getElementById(this.iconsContainerId);

        // Add action icons
        this.actions.forEach((action, index) => {
            const actionIcon = document.createElement('div');
            actionIcon.className = 'icon-button';
            actionIcon.textContent = action.icon;
            actionIcon.style.backgroundColor = '#f5f5f5';
            actionIcon.style.color = '#777';

            actionIcon.addEventListener('click', (event) => {
                event.stopPropagation();
                // Toggle action state
                action.active = !action.active;

                // Update appearance
                if (action.active) {
                    actionIcon.style.backgroundColor = action.color;
                    actionIcon.style.color = 'white';
                    actionIcon.classList.add('active');
                } else {
                    actionIcon.style.backgroundColor = '#f5f5f5';
                    actionIcon.style.color = '#777';
                    actionIcon.classList.remove('active');
                }

                // Notify parent component
                if (this.onActionToggle) {
                    this.onActionToggle(index, action.active);
                }
            });

            actionIconsContainer.appendChild(actionIcon);
        });

        // Add actions menu toggle
        actionsToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isVisible = actionsMenu.style.display === 'block';

            // Close all dropdowns first
            document.dispatchEvent(new CustomEvent('closeAllDropdowns'));

            // Then open this one if it was closed
            if (!isVisible) {
                actionsMenu.style.display = 'block';
            }
        });
    }

    /**
     * Closes the dropdown menu if it's open
     */
    closeDropdown() {
        const actionsMenu = document.getElementById(this.menuId);
        if (actionsMenu) {
            actionsMenu.style.display = 'none';
        }
    }
}