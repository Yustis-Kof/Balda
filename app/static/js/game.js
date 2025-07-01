const board = document.getElementById('board');
const wordline = document.getElementById('word')
// Пример игрового поля
const grid = [
    ['', '', '', '', ''],
    ['', '', '', '', ''],
    ['Б', 'А', 'Л', 'Д', 'А'],
    ['', '', '', '', ''],
    ['', '', '', '', '']
];

// Глобальные переменные
let isSelecting = false;
let selectedCells = [];
let currentMoveLetter = null;
let isMoveInProgress = false;
let timeForMove = 60;
let timerValue = timeForMove;
let timerInterval = null;

const players = [
    { name: "Игрок 1", words: [], score: 0 },
    { name: "Игрок 2", words: [], score: 0 }
];
let currentPlayerIndex = 0;

// Проверка сессии при загрузке
async function checkAuth() {
    const response = await fetch('/check_session');
    const data = await response.json();
    
    if (!data.authenticated) {
        window.location.href = '/login';
    }
}

// Отправка логина
async function login(username, password) {
    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    return await response.json();
}

// Выход
async function logout() {
    await fetch('/logout');
    window.location.href = '/login';
}

/**
 * Отрисовывает игровое поле
 */
function renderBoard() {
    board.innerHTML = '';
    grid.forEach((row, i) => {
        const rowElement = document.createElement('tr');
        row.forEach((cell, j) => {
            const cellElement = document.createElement('td');
            cellElement.textContent = cell === '' ? '\u00A0' : cell;
            
            if (cell === '') {
                cellElement.classList.add('empty');
            }
            
            cellElement.dataset.row = i;
            cellElement.dataset.col = j;
            cellElement.addEventListener('click', () => addLetter(i, j));
            cellElement.addEventListener('mousedown', () => startSelection(i, j));
            cellElement.addEventListener('mouseenter', () => addToSelection(i, j));
            cellElement.addEventListener('mouseup', endSelection);
            
            rowElement.appendChild(cellElement);
        });
        board.appendChild(rowElement);
    });
        updateSelection();
}

function startSelection(i, j) {
    if (grid[i][j] === '' || currentMoveLetter === null) return;
    isSelecting = true;
    selectedCells = [{ row: i, col: j }];
    updateSelection();
}

function addToSelection(i, j) {
    if (!isSelecting || grid[i][j] === '') return;

    const lastCell = selectedCells[selectedCells.length - 1];
    const rowDiff = Math.abs(i - lastCell.row);
    const colDiff = Math.abs(j - lastCell.col);

    if ((rowDiff + colDiff === 1) && !(rowDiff === 0 && colDiff === 0)) {
        if (selectedCells.length > 1) {
            const prevCell = selectedCells[selectedCells.length - 2];
            if (prevCell.row === i && prevCell.col === j) {
                selectedCells.pop();
                updateSelection();
                return;
            }
        }

        const isAlreadySelected = selectedCells.some(cell => cell.row === i && cell.col === j);
        if (!isAlreadySelected) {
            selectedCells.push({ row: i, col: j });
            updateSelection();
        }
    }
}

function endSelection() {
    if (!isSelecting) return;
    isSelecting = false;

    if (selectedCells.length > 1) {
        document.getElementById('selection-controls').style.display = 'block';
    } else {
        selectedCells = [];
        updateSelection();
    }
}

function updateSelection() {
    const cells = document.querySelectorAll('td');
    cells.forEach(cell => cell.classList.remove('selected'));

    selectedCells.forEach(cell => {
        const cellElement = document.querySelector(`td[data-row="${cell.row}"][data-col="${cell.col}"]`);
        if (cellElement) {
            cellElement.classList.add('selected');
        }
    });

    const word = selectedCells.map(cell => grid[cell.row][cell.col]).join('')
    wordline.innerHTML = word;
}

let activeInput = null;

function addLetter(i, j) {
    if (grid[i][j] !== '' || currentMoveLetter !== null) return;

    if (!isAdjacentToFilled(i, j)) {
        alert("Можно вводить только в соседние клетки!");
        return;
    }

    // Если уже есть активный ввод, завершаем его
    if (activeInput) {
        finishActiveInput();
    }

    currentMoveLetter = { row: i, col: j };
    document.getElementById('reset-button').style.display = 'block';
    isMoveInProgress = true;

    const cellElement = board.rows[i].cells[j];
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 1;

    // Обработка ввода русских букв
    input.addEventListener('input', (e) => {
        const value = e.target.value.toUpperCase();
        const russianLetters = /^[А-ЯЁ]$/;
        if (!russianLetters.test(value)) {
            e.target.value = '';
        } else {
            e.target.value = value;
        }
    });

    // При потере фокуса
    input.addEventListener('blur', (e) => {
        const value = e.target.value.toUpperCase();
        
        if (value) {
            grid[i][j] = value;
        } else {
            // Если буква не введена - сбрасываем состояние
            grid[i][j] = '';
            currentMoveLetter = null;
            isMoveInProgress = false;
            document.getElementById('reset-button').style.display = 'none';
        }
        
        activeInput = null;
        renderBoard();
    });

    // При нажатии Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const value = e.target.value.toUpperCase();
            
            if (value) {
                grid[i][j] = value;
            } else {
                // Если буква не введена - сбрасываем состояние
                grid[i][j] = '';
                currentMoveLetter = null;
                isMoveInProgress = false;
                document.getElementById('reset-button').style.display = 'none';
            }
            
            activeInput = null;
            renderBoard();
        }
    });

    cellElement.innerHTML = '';
    cellElement.appendChild(input);
    input.focus();
    activeInput = input;

    document.getElementById('selection-controls').style.display = 'none';
}

// Новая функция для завершения активного ввода
function finishActiveInput() {
    if (!activeInput) return;
    
    const cellElement = activeInput.parentElement;
    const i = parseInt(cellElement.dataset.row);
    const j = parseInt(cellElement.dataset.col);
    const value = activeInput.value.toUpperCase();
    
    if (value) {
        grid[i][j] = value;
    } else {
        // Если буква не введена - сбрасываем состояние
        grid[i][j] = '';
        currentMoveLetter = null;
        isMoveInProgress = false;
        document.getElementById('reset-button').style.display = 'none';
    }
    
    activeInput = null;
    renderBoard();
}

function isAdjacentToFilled(row, col) {
    const directions = [
        [-1, 0], [0, -1], [0, 1], [1, 0]
    ];
    return directions.some(([dr, dc]) => {
        const r = row + dr;
        const c = col + dc;
        return r >= 0 && r < 5 && c >= 0 && c < 5 && grid[r][c] !== '';
    });
}

function resetLetter() {
    if (currentMoveLetter) {
        grid[currentMoveLetter.row][currentMoveLetter.col] = '';
        currentMoveLetter = null;
        document.getElementById('reset-button').style.display = 'none';
        renderBoard();
        updateSelection();
        cancelSelection();
    }
}

function cancelSelection() {
    selectedCells = [];
    updateSelection();
    document.getElementById('selection-controls').style.display = 'none';
}

function submitWord() {
    // Проверка наличия новой буквы в слове
    if (!currentMoveLetter) {
        alert("Сначала добавьте букву!");
        return;
    }
    
    const containsNewLetter = selectedCells.some(cell => 
        cell.row === currentMoveLetter.row && 
        cell.col === currentMoveLetter.col
    );

    if (!containsNewLetter) {
        alert("Слово должно содержать новую букву!");
        return;
    }

    const word = selectedCells.map(cell => grid[cell.row][cell.col]).join('');
    sendMoveToServer(word);
    document.getElementById('selection-controls').style.display = 'none';
}

function sendMoveToServer(word) {
    fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: word })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            players[currentPlayerIndex].words.push(word);
            players[currentPlayerIndex].score += word.length;
            passTurn();
        } else {
            alert(data.message);
        }
    });
    cancelSelection();
}

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    
    timerValue = timeForMove;
    document.getElementById('timer').textContent = `Время: ${timerValue}`;
    
    timerInterval = setInterval(() => {
        timerValue--;
        document.getElementById('timer').textContent = `Время: ${timerValue}`;
        
        if (timerValue <= 0) {
            clearInterval(timerInterval);
            passTurn();
        }
    }, 1000);
}

function passTurn() {
    currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
    isMoveInProgress = false;
    currentMoveLetter = null;
    selectedCells = [];
    document.getElementById('reset-button').style.display = 'none';
    timerValue = timeForMove;
    updateScoreboard();
    startTimer();
}

function updateScoreboard() {
    players.forEach((player, index) => {
        const column = document.getElementById(`player${index+1}-column`);
        if (column) {
            column.querySelector('.word-list').innerHTML = player.words.join('<br>') || '—';
            column.querySelector('.score').textContent = player.score;
        }
    });
    
    document.querySelector('.total-score').textContent = `Всего: ${
        players.reduce((sum, player) => sum + player.score, 0)
    }`;
}

// Инициализация игры
document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        // Извлекаем ID игры из URL
        const pathParts = window.location.pathname.split('/');
        const gameId = pathParts[pathParts.length - 1];
        
        if (gameId) {
            document.getElementById('game-id').textContent = gameId;
            renderBoard();
            startTimer();
            updateScoreboard();
        } else {
            alert('Не указан ID игры');
            window.location.href = '/';
        }
    });
});