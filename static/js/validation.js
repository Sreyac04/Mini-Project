/* Book Bot - Form Validation JavaScript */

class FormValidator {
  constructor(formSelector) {
    this.form = document.querySelector(formSelector);
    this.validators = {};
    this.messages = {};
    this.init();
  }

  init() {
    if (!this.form) return;
    
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    this.setupRealTimeValidation();
  }

  // Add validation rule for a field
  addRule(fieldName, validator, message) {
    if (!this.validators[fieldName]) {
      this.validators[fieldName] = [];
      this.messages[fieldName] = [];
    }
    this.validators[fieldName].push(validator);
    this.messages[fieldName].push(message);
  }

  // Setup real-time validation
  setupRealTimeValidation() {
    const inputs = this.form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      input.addEventListener('blur', () => this.validateField(input.name));
      input.addEventListener('input', () => this.clearFieldError(input.name));
    });
  }

  // Validate a single field
  validateField(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    if (!field || !this.validators[fieldName]) return true;

    const value = field.value.trim();
    const validators = this.validators[fieldName];
    const messages = this.messages[fieldName];

    for (let i = 0; i < validators.length; i++) {
      if (!validators[i](value)) {
        this.showFieldError(fieldName, messages[i]);
        return false;
      }
    }

    this.showFieldSuccess(fieldName);
    return true;
  }

  // Validate all fields
  validateAll() {
    let isValid = true;
    Object.keys(this.validators).forEach(fieldName => {
      if (!this.validateField(fieldName)) {
        isValid = false;
      }
    });
    return isValid;
  }

  // Handle form submission
  handleSubmit(e) {
    if (!this.validateAll()) {
      e.preventDefault();
      this.showFormError('Please fix the errors above before submitting.');
      return false;
    }
    this.clearFormError();
    return true;
  }

  // Show field error
  showFieldError(fieldName, message) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = document.getElementById(`${fieldName}Error`) || 
                        this.createErrorElement(fieldName);
    
    field.classList.remove('success');
    field.classList.add('error');
    errorElement.textContent = message;
    errorElement.classList.add('show');
  }

  // Show field success
  showFieldSuccess(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = document.getElementById(`${fieldName}Error`);
    
    field.classList.remove('error');
    field.classList.add('success');
    if (errorElement) {
      errorElement.classList.remove('show');
    }
  }

  // Clear field error
  clearFieldError(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = document.getElementById(`${fieldName}Error`);
    
    field.classList.remove('error', 'success');
    if (errorElement) {
      errorElement.classList.remove('show');
    }
  }

  // Create error element if it doesn't exist
  createErrorElement(fieldName) {
    const field = this.form.querySelector(`[name="${fieldName}"]`);
    const errorElement = document.createElement('div');
    errorElement.id = `${fieldName}Error`;
    errorElement.className = 'error-message';
    field.parentNode.insertBefore(errorElement, field.nextSibling);
    return errorElement;
  }

  // Show form-level error
  showFormError(message) {
    let errorElement = document.getElementById('formError');
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.id = 'formError';
      errorElement.className = 'error-message show';
      errorElement.style.marginBottom = '1rem';
      errorElement.style.padding = '0.75rem';
      errorElement.style.backgroundColor = '#fef2f2';
      errorElement.style.border = '1px solid #fecaca';
      errorElement.style.borderRadius = '0.375rem';
      errorElement.style.fontSize = '0.875rem';
      this.form.insertBefore(errorElement, this.form.firstChild);
    }
    errorElement.textContent = message;
    errorElement.classList.add('show');
  }

  // Clear form-level error
  clearFormError() {
    const errorElement = document.getElementById('formError');
    if (errorElement) {
      errorElement.classList.remove('show');
    }
  }
}

// Common validation functions
const ValidationRules = {
  required: (value) => value.length > 0,
  
  email: (value) => {
    // RFC 5322 compliant email validation with whitespace trimming
    const emailRegex = /^(?:[a-zA-Z0-9]([a-zA-Z0-9-_.])*[a-zA-Z0-9])@([a-zA-Z0-9][a-zA-Z0-9-]*\.)+[a-zA-Z]{2,}$/;
    return emailRegex.test(value.trim());
  },
  
  minLength: (min) => (value) => value.length >= min,
  
  maxLength: (max) => (value) => value.length <= max,
  
  phone: (value) => {
    const phoneRegex = /^[\+]?[0-9]{10,15}$/;
    return phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''));
  },
  
  password: (value) => {
    // At least 8 characters, one uppercase, one lowercase, one number
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(value);
  },
  
  passwordSimple: (value) => value.length >= 6,
  
  alphabetic: (value) => {
    const nameRegex = /^[a-zA-Z\s]+$/;
    return nameRegex.test(value);
  },
  
  date: (value) => {
    const date = new Date(value);
    return date instanceof Date && !isNaN(date);
  },
  
  dateRange: (min, max) => (value) => {
    const date = new Date(value);
    const minDate = new Date(min);
    const maxDate = new Date(max);
    return date >= minDate && date <= maxDate;
  },
  
  age: (minAge) => (value) => {
    const birthDate = new Date(value);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      return (age - 1) >= minAge;
    }
    return age >= minAge;
  },
  
  match: (fieldName) => (value) => {
    const matchField = document.querySelector(`[name="${fieldName}"]`);
    return matchField && value === matchField.value;
  }
};

// Utility function to setup register form validation
function setupRegisterValidation() {
  const validator = new FormValidator('#registerForm');
  
  // Username validation
  validator.addRule('username', ValidationRules.required, 'Name is required');
  validator.addRule('username', ValidationRules.minLength(2), 'Name must be at least 2 characters');
  validator.addRule('username', ValidationRules.maxLength(50), 'Name must not exceed 50 characters');
  validator.addRule('username', ValidationRules.alphabetic, 'Name can only contain letters and spaces');
  
  // Email validation
  validator.addRule('email', ValidationRules.required, 'Email is required');
  validator.addRule('email', ValidationRules.email, 'Please enter a valid email address');
  
  // Password validation
  validator.addRule('password', ValidationRules.required, 'Password is required');
  validator.addRule('password', ValidationRules.passwordSimple, 'Password must be at least 6 characters long');
  
  // Phone validation
  validator.addRule('phone_number', ValidationRules.required, 'Phone number is required');
  validator.addRule('phone_number', ValidationRules.phone, 'Please enter a valid 10-digit phone number');
  
  // Date of birth validation
  validator.addRule('dob', ValidationRules.required, 'Date of birth is required');
  validator.addRule('dob', ValidationRules.date, 'Please enter a valid date');
  validator.addRule('dob', ValidationRules.dateRange('1960-01-01', '2015-12-31'), 'Date must be between 1960 and 2015');
  validator.addRule('dob', ValidationRules.age(8), 'You must be at least 8 years old');
  
  // Gender validation
  validator.addRule('gender', ValidationRules.required, 'Please select your gender');
  
  return validator;
}

// Utility function to setup login form validation
function setupLoginValidation() {
  const validator = new FormValidator('#loginForm');
  
  validator.addRule('email', ValidationRules.required, 'Email is required');
  validator.addRule('email', ValidationRules.email, 'Please enter a valid email address');
  validator.addRule('password', ValidationRules.required, 'Password is required');
  
  return validator;
}

// Password strength indicator
function createPasswordStrengthIndicator(passwordFieldName) {
  const passwordField = document.querySelector(`[name="${passwordFieldName}"]`);
  if (!passwordField) return;
  
  const strengthContainer = document.createElement('div');
  strengthContainer.className = 'password-strength';
  strengthContainer.innerHTML = `
    <div class="strength-bar">
      <div class="strength-fill"></div>
    </div>
    <div class="strength-text">Password Strength: <span class="strength-level">Weak</span></div>
  `;
  
  // Add CSS for password strength indicator
  const style = document.createElement('style');
  style.textContent = `
    .password-strength {
      margin-top: 0.5rem;
      font-size: 0.75rem;
    }
    .strength-bar {
      height: 4px;
      background-color: #e5e7eb;
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 0.25rem;
    }
    .strength-fill {
      height: 100%;
      transition: all 0.3s ease;
      width: 0%;
    }
    .strength-weak .strength-fill { background-color: #ef4444; width: 25%; }
    .strength-fair .strength-fill { background-color: #f59e0b; width: 50%; }
    .strength-good .strength-fill { background-color: #3b82f6; width: 75%; }
    .strength-strong .strength-fill { background-color: #10b981; width: 100%; }
  `;
  document.head.appendChild(style);
  
  passwordField.parentNode.insertBefore(strengthContainer, passwordField.nextSibling);
  
  passwordField.addEventListener('input', () => {
    const password = passwordField.value;
    const strength = calculatePasswordStrength(password);
    updatePasswordStrengthUI(strengthContainer, strength);
  });
}

function calculatePasswordStrength(password) {
  let score = 0;
  const checks = [
    password.length >= 8,
    /[a-z]/.test(password),
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password)
  ];
  
  score = checks.filter(check => check).length;
  
  if (score <= 2) return 'weak';
  if (score === 3) return 'fair';
  if (score === 4) return 'good';
  return 'strong';
}

function updatePasswordStrengthUI(container, strength) {
  const strengthLevel = container.querySelector('.strength-level');
  const strengthBar = container.querySelector('.strength-bar');
  
  // Remove old classes
  strengthBar.className = 'strength-bar';
  
  // Add new class and update text
  strengthBar.classList.add(`strength-${strength}`);
  strengthLevel.textContent = strength.charAt(0).toUpperCase() + strength.slice(1);
}

// Initialize validation when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM Content Loaded - Validation.js initializing...');
  
  // Check which form is present and initialize appropriate validation
  if (document.getElementById('registerForm')) {
    console.log('Register form found, setting up validation...');
    setupRegisterValidation();
    createPasswordStrengthIndicator('password');
    setupPasswordToggle('password');
  }
  
  if (document.getElementById('loginForm')) {
    console.log('Login form found, setting up validation...');
    setupLoginValidation();
    setupPasswordToggle('password');
  }
  
  // Initialize logout confirmation on all pages
  console.log('Setting up logout confirmation...');
  setupLogoutConfirmation();
});

// Logout confirmation function with custom modal
function confirmLogout(event) {
  event.preventDefault();
  
  // Create custom modal
  const modal = createLogoutModal();
  document.body.appendChild(modal);
  
  // Show modal
  modal.style.display = 'flex';
  
  // Handle Yes button
  const yesBtn = modal.querySelector('.logout-yes-btn');
  const noBtn = modal.querySelector('.logout-no-btn');
  
  yesBtn.onclick = function() {
    window.location.href = event.target.href;
  };
  
  // Handle No button and close modal
  noBtn.onclick = function() {
    document.body.removeChild(modal);
  };
  
  // Close modal when clicking outside
  modal.onclick = function(e) {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  };
  
  return false;
}

// Create logout confirmation modal
function createLogoutModal() {
  const modal = document.createElement('div');
  modal.className = 'logout-modal';
  modal.innerHTML = `
    <div class="logout-modal-content">
      <div class="logout-modal-header">
        <h3>Confirm Logout</h3>
      </div>
      <div class="logout-modal-body">
        <p>Are you sure you want to logout?</p>
      </div>
      <div class="logout-modal-footer">
        <button class="btn btn-primary logout-yes-btn">Yes</button>
        <button class="btn btn-outline logout-no-btn">No</button>
      </div>
    </div>
  `;
  
  return modal;
}

// Setup logout confirmation on all logout links
function setupLogoutConfirmation() {
  const logoutLinks = document.querySelectorAll('a[href*="logout"]');
  console.log('Found', logoutLinks.length, 'logout links');
  logoutLinks.forEach((link, index) => {
    console.log('Adding event listener to logout link', index + 1, ':', link.href);
    link.addEventListener('click', confirmLogout);
  });
}

// Password visibility toggle functionality
function setupPasswordToggle(passwordFieldName) {
  const passwordField = document.querySelector(`[name="${passwordFieldName}"]`);
  if (!passwordField) return;
  
  // Wrap the password field in a container
  const wrapper = document.createElement('div');
  wrapper.className = 'password-field';
  passwordField.parentNode.insertBefore(wrapper, passwordField);
  wrapper.appendChild(passwordField);
  
  // Create the toggle button
  const toggleButton = document.createElement('button');
  toggleButton.type = 'button';
  toggleButton.className = 'password-toggle';
  toggleButton.innerHTML = '👁️';
  toggleButton.setAttribute('aria-label', 'Toggle password visibility');
  
  // Add the toggle button to the wrapper
  wrapper.appendChild(toggleButton);
  
  // Add click event listener
  toggleButton.addEventListener('click', function() {
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    
    // Update the button icon
    toggleButton.innerHTML = type === 'password' ? '👁️' : '🙈';
    
    // Update aria-label
    toggleButton.setAttribute('aria-label', 
      type === 'password' ? 'Show password' : 'Hide password'
    );
  });
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FormValidator, ValidationRules, setupRegisterValidation, setupLoginValidation };
}