const tg = window.Telegram.WebApp;
tg.expand();

// Функция отправки
function submitBooking() {
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const car_number = document.getElementById('car_number').value.toUpperCase();
    const car_model = document.getElementById('car_model').value;
    
    if (!date || !time || !car_number || !car_model) {
        tg.showAlert('Заполните все поля!');
        return;
    }
    
    const data = { date, time, car_number, car_model };
    console.log('Отправляем:', data);  // Для отладки
    
    tg.sendData(JSON.stringify(data));
    tg.showAlert('Запись отправлена!');
    tg.close();
}

// Кнопка MainButton (альтернатива)
tg.MainButton.setText('📝 Записать').onClick(submitBooking).show();
