const tg = window.Telegram.WebApp;
tg.expand();

// Определяем тип услуги из URL
const urlParams = new URLSearchParams(window.location.search);
const service = urlParams.get('service') || 'wash';  // По умолчанию автомойка

// Заполняем время 9:00-21:00
const timeSelect = document.getElementById('time');
for (let h = 9; h <= 21; h++) {
    const option = document.createElement('option');
    option.value = `${h.toString().padStart(2, '0')}:00`;
    option.textContent = `${h.toString().padStart(2, '0')}:00`;
    timeSelect.appendChild(option);
}

tg.MainButton.setText('📝 Записать').onClick(submitBooking).show();

function submitBooking() {
    const data = {
        service: service,  // wash или service
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        car_model: document.getElementById('car_model').value
    };
    
    if (!data.date || !data.time || !data.car_model) {
        tg.showAlert('Заполните все поля!');
        return;
    }
    
    tg.sendData(JSON.stringify(data));
    tg.close();
}
