// Функция за изпращане на POST заявка към Flask API и зареждане на резултати на втората страница
async function submitInvestmentForm(event) {
    event.preventDefault(); // Превенция на стандартното поведение на формата

    // Вземи стойностите от формата
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const period_weeks = parseInt(document.getElementById('period_weeks').value);

    const formData = {
        start_date: start_date,
        end_date: end_date,
        amount: amount,
        period_weeks: period_weeks
    };

    try {
        // Изпращане на POST заявка с данните от формата
        const response = await fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        // Проверка дали заявката е успешна
        if (!response.ok) {
            throw new Error('Грешка при изпращането на данните');
        }

        // Получаване на отговор в JSON формат
        const data = await response.json();

        // Обработване на данните и зареждане на резултати на втората страница
        if (data) {
            const {
                investment_history,
                total_invested,
                total_btc,
                current_price,
                current_value,
                profit_loss_percentage,
                investment_status
            } = data;

            // Пример за обработка на данни и показване на резултатите (можеш да промениш това според нуждите си)
            const resultContainer = document.getElementById('investment-result');
            resultContainer.innerHTML = `
                <h2>Резултати от инвестицията</h2>
                <table border="1">
                    <thead>
                        <tr>
                            <th>Дата</th>
                            <th>Цена на биткойн</th>
                            <th>Закупено количество BTC</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${investment_history.map(item => `
                            <tr>
                                <td>${item[0]}</td>
                                <td>${item[1]}</td>
                                <td>${item[2]}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <p><strong>Общо инвестираната сума: </strong>$${total_invested}</p>
                <p><strong>Общо закупени BTC: </strong>${total_btc}</p>
                <p><strong>Текуща цена на BTC: </strong>$${current_price}</p>
                <p><strong>Текуща стойност на инвестицията: </strong>$${current_value}</p>
                <p><strong>Печалба/Загуба: </strong>${profit_loss_percentage}%</p>
                <p><strong>Статус: </strong>${investment_status}</p>
            `;
        }
    } catch (error) {
        console.error('Грешка:', error);
    }
}

// Добави обработчик на събитие за изпращането на формата
document.getElementById('investment-form').addEventListener('submit', submitInvestmentForm);
