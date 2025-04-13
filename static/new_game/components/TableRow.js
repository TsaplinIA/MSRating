/**
 * Table Row Component
 * Represents a single row in the interactive table
 */
class TableRow {
    /**
     * Creates a table row component
     * @param {number} rowId - The ID for this row
     * @param {Object} initialData - Initial data for the row
     */
    constructor(rowId, initialData = {}) {
        this.rowId = rowId;
        this.data = {
            id: rowId,
            role: initialData.role || Object.keys(ROLES)[Math.floor(Math.random() * 4)],
            nickname: initialData.nickname || '',
            actions: initialData.actions || [...ACTION_ICONS]
        };

        // Create sub-components
        this.roleSelector = new RoleSelector(
            rowId,
            this.data.role,
            (role) => this.updateRole(role)
        );

        this.nicknameEditor = new NicknameEditor(
            rowId,
            this.data.nickname,
            (nickname) => this.updateNickname(nickname)
        );

        this.actionsMenu = new ActionsMenu(
            rowId,
            this.data.actions,
            (index, active) => this.updateAction(index, active)
        );
    }

    /**
     * Renders the table row component
     * @returns {HTMLElement} The table row element
     */
    render() {
        // Create row element
        const row = document.createElement('tr');
        row.id = `row-${this.rowId}`;

        // Create cell for row ID
        const idCell = document.createElement('td');
        idCell.textContent = this.rowId;
        row.appendChild(idCell);

        // Create cell for role selector
        const roleCell = document.createElement('td');
        roleCell.innerHTML = this.roleSelector.render();
        row.appendChild(roleCell);

        // Create cell for nickname editor
        const nicknameCell = document.createElement('td');
        nicknameCell.innerHTML = this.nicknameEditor.render();
        row.appendChild(nicknameCell);

        // Create cell for actions menu
        const actionsCell = document.createElement('td');
        actionsCell.innerHTML = this.actionsMenu.render();
        row.appendChild(actionsCell);

        return row;
    }

    /**
     * Initializes the row after it's been rendered to the DOM
     */
    initialize() {
        this.roleSelector.initialize();
        this.nicknameEditor.initialize();
        this.actionsMenu.initialize();
    }

    /**
     * Updates the role of this row
     * @param {string} role - The new role
     */
    updateRole(role) {
        this.data.role = role;
        // Additional logic if needed
    }

    /**
     * Updates the nickname of this row
     * @param {string} nickname - The new nickname
     */
    updateNickname(nickname) {
        this.data.nickname = nickname;
        // Additional logic if needed
    }

    /**
     * Updates an action's state
     * @param {number} index - The index of the action
     * @param {boolean} active - Whether the action is active
     */
    updateAction(index, active) {
        if (this.data.actions[index]) {
            this.data.actions[index].active = active;
        }
        // Additional logic if needed
    }

    /**
     * Closes any open dropdowns in this row
     */
    closeDropdowns() {
        this.roleSelector.closeDropdown();
        this.actionsMenu.closeDropdown();
    }
}