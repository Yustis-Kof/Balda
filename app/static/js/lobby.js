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

function renderLobbies(lobbies) {
    const lobbyList = document.getElementById('lobby-list');
    lobbyList.innerHTML = '';
    
    lobbies.forEach(lobby => {
        const lobbyItem = document.createElement('div');
        lobbyItem.className = 'lobby-item';
        lobbyItem.dataset.id = lobby.id;
        
        lobbyItem.innerHTML = `
            <div class="lobby-header">
                <h3>${lobby.name}</h3>
                <span>${lobby.players.length}/${lobby.max_players} игроков</span>
            </div>
            <div class="player-list">
                ${lobby.players.map(player => 
                    `<div class="player">${player.username}</div>`
                ).join('')}
            </div>
            <button class="join-btn" onclick="joinLobby('${lobby.id}')">
                Присоединиться
            </button>
            <button class="start-btn" data-game-id="${lobby.id}">Начать игру</button>
        `;
        
        lobbyList.appendChild(lobbyItem);
    });
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

async function joinLobby(gameId) {
    // 1. Получаем текущего пользователя
    const userResponse = await fetch('/get_current_user');
    if (!userResponse.ok) throw new Error('Failed to get user');
    
    const userData = await userResponse.json();
    if (!userData.user_id) throw new Error('User not authenticated');
    
    // 2. Получаем данные лобби
    const gameResponse = await fetch(`/lobby/${gameId}`);
    if (!gameResponse.ok) throw new Error('Failed to get lobby');
    
    const gameData = await gameResponse.json();
    
    // 3. Проверяем, что игрок в лобби
    const playerInLobby = gameData.players.some(p => p.id === userData.user_id);
    if (!playerInLobby) throw new Error('Player not in lobby');
    
    // 4. Проверяем, является ли хостом
    const isHost = gameData.players[0].id === userData.user_id;
    
    // 5. Показываем соответствующие элементы
    if (isHost) {
        document.getElementById('start-button').classList.remove('hidden');
    } else {
        document.getElementById('waiting-section').classList.remove('hidden');
        waitForGameStart(gameId);
    }
}

let activeGameWait = null;

// Функция ожидания начала игры
function waitForGameStart(gameId) {
    if (activeGameWait) {
        clearTimeout(activeGameWait);
        activeGameWait = null;
    }
    
    fetch(`/lobby/${gameId}/wait_start`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                window.location.href = `/lobby/${gameId}`;
            } else {
                activeGameWait = setTimeout(() => waitForGameStart(gameId), 30000);
            }
        })
        .catch(error => {
            console.error('Ошибка ожидания:', error);
            activeGameWait = setTimeout(() => waitForGameStart(gameId), 5000);
        });
}

document.querySelector('.lobby-list').addEventListener('click', (e) => {
    // Проверяем, что клик был по кнопке "Начать игру"
    if (e.target.classList.contains('start-btn')) {
        const gameId = e.target.getAttribute('data-game-id');
        
        fetch(`/lobby/${gameId}/start`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = `/lobby/${gameId}`;
                }
            });
    }
});

getLobbies()

// Инициализация страницы
document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        getLobbies();
        
        // Обновление списка каждые 10 секунд
        setInterval(getLobbies, 10000);
    });
});

window.addEventListener('beforeunload', () => {
    if (activeGameWait) {
        clearTimeout(activeGameWait);
    }
});

