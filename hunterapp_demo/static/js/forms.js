/**
 * Form Manager v2.1.0
 * Handles form validation, auto-save, and user experience enhancements
 */

class FormManager {
    constructor() {
        this.forms = new Map();
        this.autoSaveInterval = null;
        this.init();
    }

    init() {
        this.setupFormValidation();
        this.setupAutoSave();
        this.setupCharacterCounters();
        this.setupFileUploads();
    }

    setupFormValidation() {
        // Real-time validation
        document.addEventListener('input', (e) => {
            if (e.target.matches('.form-control')) {
                this.validateField(e.target);
            }
        });

        // Form submission validation
        document.addEventListener('submit', (e) => {
            if (e.target.matches('form')) {
                if (!this.validateForm(e.target)) {
                    e.preventDefault();
                }
            }
        });
    }

    validateField(field) {
        const formGroup = field.closest('.form-group');
        const feedback = formGroup.querySelector('.form-feedback');
        
        // Remove existing validation classes
        formGroup.classList.remove('has-error', 'has-success');
        
        // Validate based on field type
        let isValid = true;
        let message = '';

        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
            message = 'This field is required.';
        } else if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                isValid = false;
                message = 'Please enter a valid email address.';
            }
        } else if (field.type === 'url' && field.value) {
            try {
                new URL(field.value);
            } catch {
                isValid = false;
                message = 'Please enter a valid URL.';
            }
        } else if (field.hasAttribute('minlength')) {
            const minLength = parseInt(field.getAttribute('minlength'));
            if (field.value.length < minLength) {
                isValid = false;
                message = `Minimum ${minLength} characters required.`;
            }
        } else if (field.hasAttribute('maxlength')) {
            const maxLength = parseInt(field.getAttribute('maxlength'));
            if (field.value.length > maxLength) {
                isValid = false;
                message = `Maximum ${maxLength} characters allowed.`;
            }
        }

        // Update field appearance
        if (field.value.trim()) {
            formGroup.classList.add(isValid ? 'has-success' : 'has-error');
        }

        // Update feedback message
        if (feedback) {
            feedback.textContent = message;
            feedback.className = `form-feedback ${isValid ? 'success' : 'error'}`;
        }

        return isValid;
    }

    validateForm(form) {
        const fields = form.querySelectorAll('.form-control[required]');
        let isFormValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });

        return isFormValid;
    }

    setupAutoSave() {
        // Auto-save every 30 seconds for forms with auto-save class
        this.autoSaveInterval = setInterval(() => {
            document.querySelectorAll('form.auto-save').forEach(form => {
                this.autoSaveForm(form);
            });
        }, 30000);
    }

    autoSaveForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Save to localStorage
        const formId = form.id || 'default-form';
        localStorage.setItem(`form-${formId}`, JSON.stringify(data));
        
        // Show auto-save indicator
        this.showAutoSaveIndicator(form);
    }

    showAutoSaveIndicator(form) {
        let indicator = form.querySelector('.auto-save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'auto-save-indicator';
            indicator.textContent = 'Auto-saved';
            form.appendChild(indicator);
        }

        indicator.style.display = 'block';
        indicator.style.opacity = '1';
        
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 300);
        }, 2000);
    }

    setupCharacterCounters() {
        document.querySelectorAll('.form-control[maxlength]').forEach(field => {
            const maxLength = parseInt(field.getAttribute('maxlength'));
            const formGroup = field.closest('.form-group');
            
            // Create character counter
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            formGroup.appendChild(counter);
            
            // Update counter on input
            field.addEventListener('input', () => {
                const remaining = maxLength - field.value.length;
                counter.textContent = `${remaining} characters remaining`;
                
                // Update counter color based on remaining characters
                counter.className = 'char-counter';
                if (remaining < 50) {
                    counter.classList.add('warning');
                }
                if (remaining < 10) {
                    counter.classList.add('error');
                }
            });
            
            // Initial update
            field.dispatchEvent(new Event('input'));
        });
    }

    setupFileUploads() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            const formGroup = input.closest('.form-group');
            const label = formGroup.querySelector('label');
            
            input.addEventListener('change', (e) => {
                const files = e.target.files;
                if (files.length > 0) {
                    const fileName = files[0].name;
                    label.textContent = `Selected: ${fileName}`;
                    label.style.color = 'var(--primary-dark)';
                } else {
                    label.textContent = 'Choose file...';
                    label.style.color = 'var(--neutral-dark)';
                }
            });
        });
    }

    // Public methods
    saveFormData(formId, data) {
        localStorage.setItem(`form-${formId}`, JSON.stringify(data));
    }

    loadFormData(formId) {
        const data = localStorage.getItem(`form-${formId}`);
        return data ? JSON.parse(data) : null;
    }

    clearFormData(formId) {
        localStorage.removeItem(`form-${formId}`);
    }

    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.formManager = new FormManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormManager;
}

