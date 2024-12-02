// Auto-dismiss Flash message display

document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('[role="alert"]');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('animate-fade-out');
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 3000);
    });
});



// Verify OTP Page JavaScript
document.addEventListener('DOMContentLoaded', function () {
    const otpInputs = document.querySelectorAll('.otp-input');

    // Resend OTP button
    document.getElementById('resendotp').addEventListener('click', function (event) {
        event.preventDefault();
        alert("OTP has been resent!");
    });

    // Handle paste event for the entire form
    document.getElementById('otpForm').addEventListener('paste', function (e) {
        e.preventDefault();

        // Get pasted text
        const pastedText = e.clipboardData.getData('text').trim();

        // Check if pasted text is exactly 6 digits
        if (/^\d{6}$/.test(pastedText)) {
            // Fill inputs with pasted digits
            pastedText.split('').forEach((digit, index) => {
                if (index < otpInputs.length) {
                    otpInputs[index].value = digit;
                }
            });

            // Focus on the last input
            otpInputs[otpInputs.length - 1].focus();
        } else {
            alert('Please paste a valid 6-digit OTP');
        }
    });

    // OTP Input Handling
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function (e) {
            // Only allow numeric input
            this.value = this.value.replace(/[^0-9]/g, '');

            // Auto move to the next input if a digit is entered
            if (this.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        // Handle backspace and arrow key navigation
        input.addEventListener('keydown', function (e) {
            // Move to previous input on backspace if current input is empty
            if (e.key === 'Backspace' && this.value.length === 0 && index > 0) {
                otpInputs[index - 1].focus();
            }

            // Arrow key navigation
            if (e.key === 'ArrowLeft' && index > 0) {
                otpInputs[index - 1].focus();
            }

            if (e.key === 'ArrowRight' && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });

        // Allow overwriting existing digit
        input.addEventListener('click', function () {
            this.select();
        });
    });

    // Concatenate OTP digits and add to a hidden input field before form submission
    document.getElementById('otpForm').addEventListener('submit', function (e) {
        // Concatenate the values from all OTP inputs
        let otp = '';
        const allFilled = Array.from(otpInputs).every(input => {
            const value = input.value.trim();
            if (value !== '') otp += value;
            return value !== '';
        });

        if (!allFilled) {
            e.preventDefault();
            alert('Please fill in all OTP digits');
        } else if (otp.length === 6) {
            // Add concatenated OTP to a hidden input
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'otp';
            hiddenInput.value = otp;
            this.appendChild(hiddenInput);
        } else {
            e.preventDefault();
            alert('Invalid OTP');
        }
    });
});




// Dashboard Page
 // Toggle balance visibility
 const toggleBalance = document.getElementById('toggleBalance');
 const balanceAmount = document.getElementById('wallet_balance');
 const actualBalance = document.getElementById('current_user_balance').textContent;
 let isHidden = true; // Start with true to show dots initially
 
 const numDots = actualBalance.replace(/[^\d]/g, '').length; // Removing non-digit characters (if any)
const dots = '•'.repeat(numDots); // Create a string with the correct number of dots

// Set dots initially
balanceAmount.textContent = dots;

 toggleBalance.classList.remove('hidden');

 
 toggleBalance.addEventListener('click', () => {
     isHidden = !isHidden;
     balanceAmount.textContent = isHidden ? dots : actualBalance;
 });
 