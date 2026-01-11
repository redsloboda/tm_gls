// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.MainButton.setText('📝 Записать').show();

// Функция отправки данных в бот
function submitBooking() {
    const data = {
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        car_number: document.getElementById('car_number').value.toUpperCase(),
        car_model: document.getElementById('car_model').value
    };
    
    // Проверка заполнения
    if (!data.date || !data.time || !data.car_number || !data.car_model) {
        tg.showAlert('Заполните все поля!');
        return;
    }
    
    // Отправка данных в бот
    tg.sendData(JSON.stringify(data));
    tg.close();
}
