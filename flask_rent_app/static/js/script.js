document.addEventListener('DOMContentLoaded', () => {
    const houseForm = document.getElementById('house-form');
    if (houseForm) {
        houseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(houseForm);
            const response = await fetch('/add_house', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            const messageDiv = document.getElementById('message');
            messageDiv.className = data.error ? 'error' : 'success';
            messageDiv.textContent = data.error || data.message;

            if (!data.error) {
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            }
        });
    }

    const calcForm = document.getElementById('calc-form');
    if (calcForm) {
        calcForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(calcForm);
            const response = await fetch('/calculator', {
                method: 'POST',
                body: new URLSearchParams(formData)
            });
            const data = await response.json();
            const resultDiv = document.getElementById('calc-result');
            resultDiv.className = data.error ? 'error' : 'success';
            resultDiv.textContent = data.error || data.result;
        });
    }
});
