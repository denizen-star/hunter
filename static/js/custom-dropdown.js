/**
 * Custom Dropdown Component
 * Replaces native <select> elements with fully customizable dropdowns
 */
class CustomDropdown {
    constructor(selectElement, options = {}) {
        this.selectElement = selectElement;
        this.options = {
            placeholder: options.placeholder || '-- Select --',
            onSelect: options.onSelect || null,
            ...options
        };
        
        this.isOpen = false;
        this.selectedValue = null;
        this.selectedText = this.options.placeholder;
        this.dropdownContainer = null;
        this.selectedDisplay = null;
        this.optionsPanel = null;
        this.hiddenInput = null;
        
        // Bind methods
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);
        
        this.init();
    }
    
    init() {
        if (!this.selectElement) {
            console.error('CustomDropdown: selectElement is required');
            return;
        }
        
        // Get initial selected value - check both direct options and options within optgroups
        const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
        if (selectedOption && selectedOption.value) {
            this.selectedValue = selectedOption.value;
            this.selectedText = selectedOption.textContent;
        } else {
            // If no option is selected, find the first option with a value
            for (let i = 0; i < this.selectElement.children.length; i++) {
                const child = this.selectElement.children[i];
                if (child.tagName === 'OPTGROUP') {
                    for (let j = 0; j < child.children.length; j++) {
                        const opt = child.children[j];
                        if (opt.tagName === 'OPTION' && opt.selected && opt.value) {
                            this.selectedValue = opt.value;
                            this.selectedText = opt.textContent;
                            break;
                        }
                    }
                    if (this.selectedValue) break;
                } else if (child.tagName === 'OPTION' && child.selected && child.value) {
                    this.selectedValue = child.value;
                    this.selectedText = child.textContent;
                    break;
                }
            }
        }
        
        // Build the custom dropdown HTML
        this.buildHTML();
        
        // Hide the original select element
        this.selectElement.style.display = 'none';
        this.selectElement.setAttribute('aria-hidden', 'true');
        
        // Add event listeners
        this.attachEventListeners();
    }
    
    buildHTML() {
        // Create container
        this.dropdownContainer = document.createElement('div');
        this.dropdownContainer.className = 'custom-dropdown';
        this.dropdownContainer.setAttribute('tabindex', '0');
        this.dropdownContainer.setAttribute('role', 'combobox');
        this.dropdownContainer.setAttribute('aria-expanded', 'false');
        this.dropdownContainer.setAttribute('aria-haspopup', 'listbox');
        
        // Create selected display
        this.selectedDisplay = document.createElement('div');
        this.selectedDisplay.className = 'custom-dropdown-selected';
        this.selectedDisplay.textContent = this.selectedText;
        
        // Create options panel
        this.optionsPanel = document.createElement('div');
        this.optionsPanel.className = 'custom-dropdown-options';
        this.optionsPanel.setAttribute('role', 'listbox');
        
        // Build options from select element
        this.buildOptions();
        
        // Create hidden input for form submission
        this.hiddenInput = document.createElement('input');
        this.hiddenInput.type = 'hidden';
        this.hiddenInput.name = this.selectElement.name || this.selectElement.id;
        this.hiddenInput.value = this.selectedValue || '';
        
        // Assemble structure
        this.dropdownContainer.appendChild(this.selectedDisplay);
        this.dropdownContainer.appendChild(this.optionsPanel);
        
        // Insert after the select element
        this.selectElement.parentNode.insertBefore(this.dropdownContainer, this.selectElement.nextSibling);
        this.selectElement.parentNode.insertBefore(this.hiddenInput, this.selectElement.nextSibling);
    }
    
    buildOptions() {
        this.optionsPanel.innerHTML = '';
        
        // Iterate through children (includes both optgroups and direct options)
        for (let i = 0; i < this.selectElement.children.length; i++) {
            const child = this.selectElement.children[i];
            
            // Handle optgroups
            if (child.tagName === 'OPTGROUP') {
                // Create optgroup container
                const optgroupContainer = document.createElement('div');
                optgroupContainer.className = 'custom-dropdown-optgroup';
                
                // Create optgroup label
                const optgroupLabel = document.createElement('div');
                optgroupLabel.className = 'custom-dropdown-optgroup-label';
                optgroupLabel.textContent = child.label;
                optgroupContainer.appendChild(optgroupLabel);
                
                // Add options within this optgroup
                for (let j = 0; j < child.children.length; j++) {
                    const opt = child.children[j];
                    if (opt.tagName === 'OPTION') {
                        // Skip empty placeholder options
                        if (!opt.value && opt.textContent.trim() === '') {
                            continue;
                        }
                        const optionElement = this.createOptionElement(opt.value, opt.textContent, opt.selected);
                        optgroupContainer.appendChild(optionElement);
                    }
                }
                
                // Only append optgroup if it has options
                if (optgroupContainer.children.length > 1) { // More than just the label
                    this.optionsPanel.appendChild(optgroupContainer);
                }
            } else if (child.tagName === 'OPTION') {
                // Regular option (not in an optgroup)
                // Skip empty placeholder options
                if (!child.value && child.textContent.trim() === '') {
                    continue;
                }
                const optionElement = this.createOptionElement(child.value, child.textContent, child.selected);
                this.optionsPanel.appendChild(optionElement);
            }
        }
    }
    
    createOptionElement(value, text, isSelected = false) {
        const optionElement = document.createElement('div');
        optionElement.className = 'custom-dropdown-option';
        optionElement.setAttribute('role', 'option');
        optionElement.setAttribute('data-value', value);
        optionElement.textContent = text;
        
        if (isSelected) {
            optionElement.classList.add('selected');
            this.selectedValue = value;
            this.selectedText = text;
        }
        
        // Add click handler
        optionElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectOption(optionElement);
        });
        
        return optionElement;
    }
    
    attachEventListeners() {
        // Toggle dropdown on click
        this.selectedDisplay.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Keyboard navigation
        this.dropdownContainer.addEventListener('keydown', this.handleKeydown);
        
        // Click outside to close
        document.addEventListener('click', this.handleClickOutside);
    }
    
    toggle() {
        this.isOpen = !this.isOpen;
        this.updateDisplay();
    }
    
    open() {
        this.isOpen = true;
        this.updateDisplay();
    }
    
    close() {
        this.isOpen = false;
        this.updateDisplay();
    }
    
    updateDisplay() {
        if (this.isOpen) {
            this.dropdownContainer.classList.add('open');
            this.optionsPanel.style.display = 'block';
            this.dropdownContainer.setAttribute('aria-expanded', 'true');
        } else {
            this.dropdownContainer.classList.remove('open');
            this.optionsPanel.style.display = 'none';
            this.dropdownContainer.setAttribute('aria-expanded', 'false');
        }
    }
    
    selectOption(optionElement) {
        // Remove previous selection
        const previousSelected = this.optionsPanel.querySelector('.custom-dropdown-option.selected');
        if (previousSelected) {
            previousSelected.classList.remove('selected');
        }
        
        // Mark as selected
        optionElement.classList.add('selected');
        
        // Update values
        this.selectedValue = optionElement.getAttribute('data-value');
        this.selectedText = optionElement.textContent;
        this.selectedDisplay.textContent = this.selectedText;
        
        // Update hidden input
        this.hiddenInput.value = this.selectedValue;
        
        // Update original select element
        this.selectElement.value = this.selectedValue;
        
        // Trigger change event on select element for compatibility
        const changeEvent = new Event('change', { bubbles: true });
        this.selectElement.dispatchEvent(changeEvent);
        
        // Call custom onSelect callback
        if (this.options.onSelect) {
            this.options.onSelect(this.selectedValue, this.selectedText);
        }
        
        // Close dropdown
        this.close();
    }
    
    handleKeydown(e) {
        if (!this.isOpen) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.open();
                return;
            }
        }
        
        if (this.isOpen) {
            const options = Array.from(this.optionsPanel.querySelectorAll('.custom-dropdown-option'));
            const currentSelected = this.optionsPanel.querySelector('.custom-dropdown-option.selected');
            let currentIndex = currentSelected ? options.indexOf(currentSelected) : -1;
            
            switch (e.key) {
                case 'Escape':
                    e.preventDefault();
                    this.close();
                    break;
                    
                case 'ArrowDown':
                    e.preventDefault();
                    currentIndex = (currentIndex + 1) % options.length;
                    this.highlightOption(options[currentIndex]);
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    currentIndex = currentIndex <= 0 ? options.length - 1 : currentIndex - 1;
                    this.highlightOption(options[currentIndex]);
                    break;
                    
                case 'Enter':
                    e.preventDefault();
                    if (currentSelected) {
                        this.selectOption(currentSelected);
                    }
                    break;
            }
        }
    }
    
    highlightOption(optionElement) {
        // Remove previous highlight
        const previousHighlighted = this.optionsPanel.querySelector('.custom-dropdown-option.highlighted');
        if (previousHighlighted) {
            previousHighlighted.classList.remove('highlighted');
        }
        
        // Add highlight
        if (optionElement) {
            optionElement.classList.add('highlighted');
            optionElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }
    
    handleClickOutside(e) {
        if (this.isOpen && !this.dropdownContainer.contains(e.target)) {
            this.close();
        }
    }
    
    updateOptions(newOptions) {
        // Clear existing options
        this.selectElement.innerHTML = '';
        
        // Add new options
        if (Array.isArray(newOptions)) {
            newOptions.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.value || opt.id || '';
                option.textContent = opt.text || opt.title || opt.name || '';
                if (opt.selected) {
                    option.selected = true;
                }
                this.selectElement.appendChild(option);
            });
        } else if (typeof newOptions === 'string') {
            // If it's HTML string, set innerHTML
            this.selectElement.innerHTML = newOptions;
        }
        
        // Rebuild custom dropdown
        this.buildOptions();
        
        // Update selected value
        const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
        if (selectedOption) {
            this.selectedValue = selectedOption.value;
            this.selectedText = selectedOption.textContent;
            this.selectedDisplay.textContent = this.selectedText;
            this.hiddenInput.value = this.selectedValue;
        } else {
            this.selectedValue = null;
            this.selectedText = this.options.placeholder;
            this.selectedDisplay.textContent = this.selectedText;
            this.hiddenInput.value = '';
        }
    }
    
    getValue() {
        return this.selectedValue;
    }
    
    setValue(value) {
        const optionElement = this.optionsPanel.querySelector(`[data-value="${value}"]`);
        if (optionElement) {
            this.selectOption(optionElement);
        }
    }
    
    destroy() {
        // Remove event listeners
        document.removeEventListener('click', this.handleClickOutside);
        
        // Remove custom dropdown elements
        if (this.dropdownContainer) {
            this.dropdownContainer.remove();
        }
        if (this.hiddenInput) {
            this.hiddenInput.remove();
        }
        
        // Show original select
        this.selectElement.style.display = '';
        this.selectElement.removeAttribute('aria-hidden');
    }
}

// Auto-initialize dropdowns with data-custom-dropdown attribute
document.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select[data-custom-dropdown]');
    selects.forEach(select => {
        new CustomDropdown(select);
    });
});

