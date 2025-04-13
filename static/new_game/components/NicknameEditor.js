/**
 * Nickname Editor Component
 * Handles the nickname editing functionality for a table row
 */
class NicknameEditor {
    /**
     * Creates a nickname editor component
     * @param {number} rowId - The ID of the row this editor belongs to
     * @param {string} initialNickname - The initial nickname value
     * @param {Function} onNicknameChange - Callback when nickname changes
     */
    constructor(rowId, initialNickname, onNicknameChange) {
        this.rowId = rowId;
        this.nickname = initialNickname || '';
        this.onNicknameChange = onNicknameChange;
        this.containerId = `nickname-container-${rowId}`;
        this.buttonId = `nickname-button-${rowId}`;
        this.inputId = `nickname-input-${rowId}`;
        this.saveButtonId = `save-nickname-${rowId}`;
        this.isEditing = false;
    }

    /**
     * Renders the nickname editor component
     * @returns {string} The HTML for the nickname editor
     */
    render() {
        return `
            <div id="${this.containerId}">
                <button class="nickname-button" id="${this.buttonId}">
                    ${this.nickname || 'Set Nickname'}
                </button>
            </div>
        `;
    }

    /**
     * Initializes the component after it's been rendered to the DOM
     */
    initialize() {
        const nicknameButton = document.getElementById(this.buttonId);
        nicknameButton.addEventListener('click', () => this.startEditing());
    }

    /**
     * Starts the nickname editing process
     */
    startEditing() {
        this.isEditing = true;
        const nicknameContainer = document.getElementById(this.containerId);

        // Create input field
        const inputContainer = document.createElement('div');
        inputContainer.innerHTML = `
            <input class="nickname-input" id="${this.inputId}" value="${this.nickname}">
            <button class="nickname-button" id="${this.saveButtonId}">Save</button>
        `;

        // Replace button with input
        nicknameContainer.innerHTML = '';
        nicknameContainer.appendChild(inputContainer);

        // Focus input
        const input = document.getElementById(this.inputId);
        input.focus();

        // Add save functionality
        const saveButton = document.getElementById(this.saveButtonId);
        saveButton.addEventListener('click', () => this.saveNickname());
        input.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                this.saveNickname();
            }
        });
    }

    /**
     * Saves the edited nickname
     */
    saveNickname() {
        const input = document.getElementById(this.inputId);
        const newNickname = input.value;
        this.nickname = newNickname;
        this.isEditing = false;

        // Restore button with new nickname
        const nicknameContainer = document.getElementById(this.containerId);
        nicknameContainer.innerHTML = '';
        const newButton = document.createElement('button');
        newButton.className = 'nickname-button';
        newButton.id = this.buttonId;
        newButton.textContent = newNickname || 'Set Nickname';
        newButton.addEventListener('click', () => this.startEditing());
        nicknameContainer.appendChild(newButton);

        // Notify parent component
        if (this.onNicknameChange) {
            this.onNicknameChange(newNickname);
        }
    }
}