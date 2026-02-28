document.addEventListener('DOMContentLoaded', function() {
    initAddToCart();
    initDiabetesToggle();
    initFormValidation();
    initHealthWarnings();
});

function initAddToCart() {
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');

    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', async function() {
            const itemId = this.getAttribute('data-item-id');
            const originalText = this.textContent;

            this.disabled = true;
            this.textContent = 'Adding...';

            try {
                const response = await fetch(`/add_to_cart/${itemId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('✅ Item added to cart!', 'success');
                    this.textContent = '✓ Added!';
                    this.classList.add('btn-success');
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.classList.remove('btn-success');
                        this.disabled = false;
                    }, 2000);
                    updateCartCount();
                } else {
                    throw new Error('Failed to add item');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('❌ Failed to add item', 'error');
                this.textContent = originalText;
                this.disabled = false;
            }
        });
    });
}

async function updateQuantity(cartId, newQuantity) {
    if (newQuantity < 1) {
        if (!confirm('Remove this item from cart?')) {
            return;
        }
        await removeItem(cartId);
        return;
    }

    try {
        const response = await fetch(`/update_cart/${cartId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantity: newQuantity })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Cart updated', 'success');
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to update quantity', 'error');
    }
}

async function removeItem(cartId) {
    try {
        const response = await fetch(`/remove_from_cart/${cartId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Item removed from cart', 'success');
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to remove item', 'error');
    }
}

function showNotification(message, type = 'info') {
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.textContent = message;

    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '10000',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        fontSize: '0.95rem',
        fontWeight: '500',
        minWidth: '250px',
        maxWidth: '400px',
        animation: 'slideInRight 0.3s ease',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
    });

    if (type === 'success') {
        notification.style.background = '#d4edda';
        notification.style.color = '#155724';
        notification.style.border = '1px solid #c3e6cb';
    } else if (type === 'error') {
        notification.style.background = '#f8d7da';
        notification.style.color = '#721c24';
        notification.style.border = '1px solid #f5c6cb';
    } else if (type === 'warning') {
        notification.style.background = '#fff3cd';
        notification.style.color = '#856404';
        notification.style.border = '1px solid #ffeaa7';
    } else {
        notification.style.background = '#d1ecf1';
        notification.style.color = '#0c5460';
        notification.style.border = '1px solid #bee5eb';
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .btn-success {
        background-color: #27ae60 !important;
    }
`;
document.head.appendChild(style);

function updateCartCount() {
    const cartLink = document.querySelector('.cart-link');
    if (cartLink) {
        console.log('Cart updated');
    }
}

function initDiabetesToggle() {
    const diabetesCheck = document.getElementById('diabetes-check');
    const diabetesType = document.getElementById('diabetes-type');

    if (diabetesCheck && diabetesType) {
        diabetesCheck.addEventListener('change', function() {
            if (this.checked) {
                diabetesType.style.display = 'block';
                diabetesType.style.animation = 'fadeIn 0.3s ease';
            } else {
                diabetesType.style.display = 'none';
            }
        });
    }
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            let firstInvalidField = null;

            requiredFields.forEach(field => {
                field.style.borderColor = '';

                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e74c3c';
                    field.style.borderWidth = '2px';

                    if (!firstInvalidField) {
                        firstInvalidField = field;
                    }
                } else {
                    field.style.borderColor = '#27ae60';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('⚠️ Please fill in all required fields', 'warning');

                if (firstInvalidField) {
                    firstInvalidField.focus();
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });

        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.style.borderColor = '#e74c3c';
                    this.style.borderWidth = '2px';
                } else if (this.value.trim()) {
                    this.style.borderColor = '#27ae60';
                    this.style.borderWidth = '2px';
                }
            });

            input.addEventListener('focus', function() {
                this.style.borderColor = '#3498db';
                this.style.borderWidth = '2px';
            });
        });
    });
}

function initHealthWarnings() {
    const warningCards = document.querySelectorAll('.warning-card');

    warningCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const warnings = this.querySelector('.health-warnings');
            if (warnings) {
                warnings.style.animation = 'pulse 0.5s ease';
            }
        });
    });
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

function initAutoSave() {
    const profileForm = document.querySelector('.profile-form');

    if (profileForm) {
        let autoSaveTimeout;
        const inputs = profileForm.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(autoSaveTimeout);

                autoSaveTimeout = setTimeout(() => {
                    const formData = new FormData(profileForm);
                    const draftData = {};

                    for (let [key, value] of formData.entries()) {
                        draftData[key] = value;
                    }

                    localStorage.setItem('profileDraft', JSON.stringify(draftData));
                    console.log('Draft saved');
                }, 2000);
            });
        });
    }
}

function initBMICalculator() {
    const weightInput = document.querySelector('input[name="weight"]');
    const heightInput = document.querySelector('input[name="height"]');
    const bmiDisplay = document.querySelector('.stat-value');

    if (weightInput && heightInput) {
        const calculateBMI = () => {
            const weight = parseFloat(weightInput.value);
            const height = parseFloat(heightInput.value);

            if (weight > 0 && height > 0) {
                const bmi = weight / ((height / 100) ** 2);
                console.log(`BMI: ${bmi.toFixed(1)}`);
            }
        };

        weightInput.addEventListener('input', calculateBMI);
        heightInput.addEventListener('input', calculateBMI);
    }
}

document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.click();
            showNotification('💾 Saving...', 'info');
        }
    }
});
