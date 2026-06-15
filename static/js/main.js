document.addEventListener('DOMContentLoaded', () => {
  // Live Currency Preview tool
  const amountInputs = document.querySelectorAll('input[name="amount"], input[name="target_amount"]');
  
  // Read exchange rate if exposed globally in templates, default to 83.0
  const exchangeRate = window.EXCHANGE_RATE_USD_TO_INR || 83.0;

  amountInputs.forEach(input => {
    // Create preview container
    const previewDiv = document.createElement('div');
    previewDiv.className = 'currency-estimate';
    previewDiv.style.display = 'none';
    input.parentNode.appendChild(previewDiv);

    const updatePreview = () => {
      const val = parseFloat(input.value);
      if (!isNaN(val) && val >= 0) {
        const usdVal = val / exchangeRate;
        previewDiv.innerHTML = `<span class="text-indigo-300">⚡ Equivalent: $${usdVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</span>`;
        previewDiv.style.display = 'block';
      } else {
        previewDiv.style.display = 'none';
      }
    };

    input.addEventListener('input', updatePreview);
    // Initial trigger if input has pre-filled value
    if (input.value) {
      updatePreview();
    }
  });

  // Dynamic animation/interaction helpers
  const glassCards = document.querySelectorAll('.bg-card');
  glassCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-4px)';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
    });
  });
});
