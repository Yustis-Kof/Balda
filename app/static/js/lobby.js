// Проверка авторизации
async function checkAuth() {
    const response = await fetch('/check_session');
    const data = await response.json();
    
    if (!data.authenticated) {
        window.location.href = '/login';
    }
}

// Выход
async function logout() {
    await fetch('/logout');
    window.location.href = '/login';
}

// Получение списка лобби
async function getLobbies() {
    try {
        const response = await fetch('/get_lobbies');
        const lobbies = await response.json();
        renderLobbies(lobbies);
    } catch (error) {
        console.error('Ошибка при загрузке лобби:', error);
        document.getElementById('lobby-list').innerHTML = 
            '<div class="error">Не удалось загрузить список лобби</div>';
    }
}

// Отображение списка лобби
function renderLobbies(lobbies) {
    const lobbyList = document.getElementById('lobby-list');
    
    if (lobbies.length === 0) {
        lobbyList.innerHTML = '<div class="empty">Нет активных лобби</div>';
        return;
    }
    
    let html = '';
    lobbies.forEach(lobby => {
        html += `
        <div class="lobby-item" data-id="${lobby.id}">
            <div class="lobby-info">
                <h3>${lobby.name}</h3>
                <span>Игроки: ${lobby.players}/${lobby.max_players}</span>
            </div>
            <button class="join-btn" onclick="joinLobby('${lobby.id}')">Присоединиться</button>
        </div>`;
    });
    
    lobbyList.innerHTML = html;
}

// Создание лобби
async function createLobby() {
    const nameInput = document.getElementById('lobby-name');
    const name = nameInput.value.trim();
    
    if (!name) {
        alert('Введите название лобби');
        return;
    }
    
    try {
        const response = await fetch('/create_lobby', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            joinLobby(data.game_id);
        } else {
            alert('Ошибка при создании лобби: ' + (data.message || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка при создании лобби:', error);
        alert('Не удалось создать лобби');
    }
}

// Присоединение к лобби
function joinLobby(gameId) {
    window.location.href = `/lobby/${gameId}`;
}

// Инициализация страницы
document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        getLobbies();
        
        // Обновление списка каждые 10 секунд
        setInterval(getLobbies, 10000);
    });
});

getLobbies()