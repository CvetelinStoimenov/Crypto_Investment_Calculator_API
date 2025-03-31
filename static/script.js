// Wait for the DOM to fully load before executing the script
document.addEventListener('DOMContentLoaded', () => {
    // Get references to the form and results container elements
    const form = document.getElementById('investment-form');       // The investment input form
    const container = document.getElementById('results-container'); // The container for displaying results
    const submitBtn = form.querySelector('.btn');                 // The submit button within the form

    // Initially hide the results container
    container.style.display = 'none';  // Ensures the results section is hidden until data is ready

    // Add event listener for form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();  // Prevent default form submission (page reload)

        // Show loading state to indicate processing
        form.classList.add('loading');       // Add 'loading' class to visually disable form
        submitBtn.disabled = true;           // Disable the submit button during processing
        submitBtn.textContent = 'Изчисляване...';  // Change button text to indicate calculation

        try {
            // Collect form data for submission
            const formData = new FormData(form);  // Create a FormData object from the form inputs

            // Send POST request to the Flask backend
            const response = await fetch('/', {
                method: 'POST',          // Use POST method to send data
                body: formData,          // Send form data as the request body
                headers: {
                    'Accept': 'application/json'  // Expect JSON response from server
                }
            });

            // Check if the response was successful
            if (!response.ok) throw new Error('Network response was not ok');  // Throw error if status isn’t 200-299

            // Parse the JSON response from the server
            const data = await response.json();

            // Handle server-side errors
            if (data.error) {
                showErrorMessage(data.error);  // Display error message if server returned an error
                return;                        // Exit the function early
            }

            // Switch UI: hide form and show results
            form.style.display = 'none';       // Hide the form after successful submission
            container.style.display = 'block'; // Show the results container

            // Render the results in the container
            displayResults(data);  // Call function to populate results

        } catch (error) {
            // Handle any errors during fetch or processing
            showErrorMessage('Възникна грешка при изчислението. Моля, опитайте отново.');  // Show generic error message
            console.error('Error:', error);  // Log error details to console for debugging
        } finally {
            // Reset loading state regardless of success or failure
            form.classList.remove('loading');  // Remove 'loading' class to re-enable form styling
            submitBtn.disabled = false;        // Re-enable the submit button
            submitBtn.textContent = 'Изчисли'; // Restore original button text
        }
    });

    // Function to display investment results
    function displayResults(data) {
        // Populate the results container with HTML based on the response data
        container.innerHTML = `
            <div class="result-summary">
                <!-- Left column: Summary of key metrics -->
                <div class="result-summary-left">
                    <div><strong>📈 Текуща цена на биткойн:</strong> $${data.current_price}</div>           <!-- Current Bitcoin price -->
                    <div><strong>💸 Средна цена на закупуване:</strong> $${data.average_purchase_price}</div>  <!-- Average purchase price -->
                    <div><strong>🔹 Общо закупени биткойни:</strong> ${data.total_btc} BTC</div>         <!-- Total BTC purchased -->
                    <div><strong>💰 Общо инвестирана сума:</strong> $${data.total_invested}</div>        <!-- Total invested amount -->
                    <div><strong>💎 Стойност на инвестицията:</strong> $${data.current_value}</div>      <!-- Current value of investment -->
                    <div><strong>📊 Процент на печалба/загуба:</strong> ${data.profit_loss_percentage}%</div>  <!-- Profit/loss percentage -->
                </div>
                <!-- Right column: Profit/loss status -->
                <div class="result-summary-right">
                    <!-- Conditionally apply 'profit' or 'loss' class based on investment status -->
                    <div class="${data.investment_status === 'ПЕЧАЛБА' ? 'profit' : 'loss'}">
                        <strong>✅ Инвестицията е на ${data.investment_status}!</strong> 🚀  <!-- Display profit or loss status -->
                    </div>
                </div>
                <!-- Button to reset the page -->
                <button onclick="resetPage()" class="btn">Ново Изчисление</button>
            </div>
            <div class="results">
                <h2>📊 История на инвестициите</h2>  <!-- Section title for investment history -->
                <table>
                    <thead>
                        <tr>
                            <th>Дата</th>              <!-- Column header: Date -->
                            <th>Цена на биткойн</th>   <!-- Column header: Bitcoin price -->
                            <th>Закупено количество</th>  <!-- Column header: Purchased amount -->
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Dynamically generate table rows from investment history -->
                        ${data.investment_history.map(row => `
                            <tr>
                                <td>${row[0]}</td>  <!-- Date of purchase -->
                                <td>${row[1]}</td>  <!-- Price at purchase -->
                                <td>${row[2]}</td>  <!-- Amount of BTC purchased -->
                            </tr>
                        `).join('')}  <!-- Join array of rows into a single string -->
                    </tbody>
                </table>
            </div>
        `;

        // Add fade-in animation for the results
        container.style.opacity = '0';  // Start with invisible container
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease-in';  // Define transition effect
            container.style.opacity = '1';                        // Fade in over 0.5 seconds
        }, 10);  // Small delay to ensure transition applies
    }

    // Function to reset the page to the initial state
    window.resetPage = function() {
        container.style.display = 'none';  // Hide the results container
        form.style.display = 'block';      // Show the form again
        container.innerHTML = '';          // Clear the results content
    };

    // Function to display error messages
    function showErrorMessage(message) {
        // Create a new div for the error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message top-error';  // Apply styling classes
        errorDiv.textContent = message;                  // Set the error message text
        // Insert the error div at the top of the page
        document.body.insertBefore(errorDiv, document.body.firstChild);
        // Automatically remove the error message after 5 seconds
        setTimeout(() => errorDiv.remove(), 5000);
    }
});