// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('investment-form');
    const container = document.getElementById('results-container');
    const submitBtn = form.querySelector('.btn');

    // Initially hide container
    container.style.display = 'none';

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        form.classList.add('loading');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Изчисляване...';

        try {
            const formData = new FormData(form);
            const response = await fetch('/', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();

            if (data.error) {
                showErrorMessage(data.error);
                return;
            }

            // Hide form and show results
            form.style.display = 'none';
            container.style.display = 'block';

            // Display results from JSON
            displayResults(data);

        } catch (error) {
            showErrorMessage('Възникна грешка при изчислението. Моля, опитайте отново.');
            console.error('Error:', error);
        } finally {
            // Remove loading state
            form.classList.remove('loading');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Изчисли';
        }
    });

    // Function to display results
    function displayResults(data) {
        container.innerHTML = `
            <div class="result-summary">
                <div class="result-summary-left">
                    <div><strong>📈 Текуща цена на биткойн:</strong> $${data.current_price}</div>
                    <div><strong>💸 Средна цена на закупуване:</strong> $${data.average_purchase_price}</div>
                    <div><strong>🔹 Общо закупени биткойни:</strong> ${data.total_btc} BTC</div>
                    <div><strong>💰 Общо инвестирана сума:</strong> $${data.total_invested}</div>
                    <div><strong>💎 Стойност на инвестицията:</strong> $${data.current_value}</div>
                    <div><strong>📊 Процент на печалба/загуба:</strong> ${data.profit_loss_percentage}%</div>
                </div>
                <div class="result-summary-right">
                    <div class="${data.investment_status === 'ПЕЧАЛБА' ? 'profit' : 'loss'}">
                        <strong>✅ Инвестицията е на ${data.investment_status}!</strong> 🚀
                    </div>
                </div>
                <button onclick="resetPage()" class="btn">Ново Изчисление</button>
            </div>
            <div class="results">
                <h2>📊 История на инвестициите</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Цена на биткойн</th>
                            <th>Закупено количество</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.investment_history.map(row => `
                            <tr>
                                <td>${row[0]}</td>
                                <td>${row[1]}</td>
                                <td>${row[2]}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Animate in
        container.style.opacity = '0';
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease-in';
            container.style.opacity = '1';
        }, 10);
    }

    // Reset page function
    window.resetPage = function() {
        container.style.display = 'none';
        form.style.display = 'block';
        container.innerHTML = '';
    };

    // Show error message
    function showErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message top-error';
        errorDiv.textContent = message;
        document.body.insertBefore(errorDiv, document.body.firstChild);
        setTimeout(() => errorDiv.remove(), 5000);
    }
});