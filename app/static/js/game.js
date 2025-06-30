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
let isSelecting = false; // Флаг для отслеживания процесса выбора
let selectedCells = []; // Массив для хранения выбранных клеток

let currentMoveLetter = null; // Координаты текущей буквы {row, col}
let isMoveInProgress = false; // Идёт ли ход
let timeForMove = 60;
let timerValue = timeForMove; // Время хода
let timerInterval = null; // Интервал таймера

const players = [
    { name: "Игрок 1", words: [], score: 0 },
    { name: "Игрок 2", words: [], score: 0 }
];
let currentPlayerIndex = 0; // Индекс текущего игрока


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
 * Отрисовывает игровое поле в теге #board
 */
function renderBoard() {
    board.innerHTML = '';
    grid.forEach((row, i) => {
        const rowElement = document.createElement('tr');
        row.forEach((cell, j) => {
            const cellElement = document.createElement('td');
            cellElement.textContent = cell;
            if (cell === '') {
                cellElement.classList.add('empty');
            }
            cellElement.addEventListener('click', () => addLetter(i, j));
            cellElement.dataset.row = i; // Добавляем данные о строке
            cellElement.dataset.col = j; // Добавляем данные о столбце
            cellElement.addEventListener('mousedown', () => startSelection(i, j));
            cellElement.addEventListener('mouseenter', () => addToSelection(i, j));
            cellElement.addEventListener('mouseup', endSelection);
            document.addEventListener('mouseup', endSelection);
            rowElement.appendChild(cellElement);
        });
        board.appendChild(rowElement);
    });
}

/**
 * Начало выбора
 * @param {number} i 
 * @param {number} j 
 */
function startSelection(i, j) {
    if (grid[i][j] === '') return; // Не начинаем выбор с пустой клетки
    isSelecting = true;
    selectedCells = [{ row: i, col: j }]; // Начинаем с текущей клетки
    updateSelection();
}

/**
 * Продолжение выбора
 * @param {number} i 
 * @param {number} j 
 */
function addToSelection(i, j) {
    if (!isSelecting || grid[i][j] === '') return; // Не добавляем пустые клетки

    const lastCell = selectedCells[selectedCells.length - 1];
    const rowDiff = Math.abs(i - lastCell.row);
    const colDiff = Math.abs(j - lastCell.col);

    // Проверяем, что клетка смежная (по горизонтали, вертикали или диагонали)
    if ((rowDiff + colDiff == 1) && !(rowDiff === 0 && colDiff === 0)) {
        // Проверяем, что клетка — это предпоследняя выбранная клетка
        if (selectedCells.length > 1) {
            const prevCell = selectedCells[selectedCells.length - 2];
            if (prevCell.row === i && prevCell.col === j) {
                // Если навели на предпоследнюю клетку, отменяем последний выбор
                selectedCells.pop(); // Удаляем последнюю клетку
                updateSelection();
                return;
            }
        }

        // Проверяем, что клетка еще не выбрана
        const isAlreadySelected = selectedCells.some(cell => cell.row === i && cell.col === j);
        if (!isAlreadySelected) {
            // Иначе добавляем клетку в выбор
            selectedCells.push({ row: i, col: j });
            updateSelection();
        }
    }
}

/**
 * Завершение выбора. Отправляет слово на проверку
 */
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

/**
 * Обновление выбора для рендера
 */
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

let activeInput = null; // Глобальная переменная для отслеживания активного поля ввода

/**
 * Создаёт в указанной клетке текстовое поле длиной
 * в 1 символ, которое удаляется при потере фокуса
 * @param {number} i 
 * @param {number} j 
 */
function addLetter(i, j) {
    if (grid[i][j] !== '' || currentMoveLetter != null) return;

    // Проверка граничащих клеток
    if (!isAdjacentToFilled(i, j)) {
        alert("Можно вводить только в соседние клетки!");
        return;
    }

    // Если уже есть активная буква, очистить её
    if (currentMoveLetter) {
        const prevRow = currentMoveLetter.row;
        const prevCol = currentMoveLetter.col;
        grid[prevRow][prevCol] = '';
        renderBoard();
    }

    // Добавление новой буквы
    currentMoveLetter = { row: i, col: j };
    document.getElementById('reset-button').style.display = 'block';
    isMoveInProgress = true;

    // Если есть активное поле ввода, завершаем его работу
    if (activeInput) {
        const currentCell = activeInput.parentElement;
        const currentRow = parseInt(currentCell.dataset.row);
        const currentCol = parseInt(currentCell.dataset.col);

        // Сохраняем значение из текущего поля ввода
        const value = activeInput.value.toUpperCase();
        if (value) {
            grid[currentRow][currentCol] = value; // Обновляем значение в сетке
        } else {
            grid[currentRow][currentCol] = "";
        }

        // Удаляем поле ввода
        currentCell.innerHTML = grid[currentRow][currentCol];
        activeInput = null; // Сбрасываем активное поле ввода
    }

    // Добавляем новое поле ввода
    const cellElement = board.rows[i].cells[j];
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 1;

    // Ограничиваем ввод только русскими буквами
    input.addEventListener('input', (e) => {
        const value = e.target.value.toUpperCase();
        const russianLetters = /^[А-ЯЁ]$/;
        if (!russianLetters.test(value)) {
            e.target.value = ''; // Очищаем ввод, если символ не русская буква
        } else {
            e.target.value = value; // Преобразуем в заглавную букву
        }
    });

    // При потере фокуса сохраняем букву в клетке
    input.addEventListener('blur', (e) => {
        const value = e.target.value.toUpperCase();
        
        if (value) {
            grid[i][j] = value;
        } else {
            grid[i][j] = "";
            // Сбрасываем состояние хода, если буква не введена
            if (currentMoveLetter && currentMoveLetter.row === i && currentMoveLetter.col === j) {
                currentMoveLetter = null;
                isMoveInProgress = false;
                //document.getElementById('reset-button').style.display = 'none';
            }
        }
        
        activeInput = null;
        renderBoard();
    });

    // При нажатии Enter сохраняем букву в клетке
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const value = e.target.value.toUpperCase();
            if (value) {
                grid[i][j] = value;
            } else {
                grid[i][j] = "";
                // Сбрасываем состояние хода, если буква не введена
                if (currentMoveLetter && currentMoveLetter.row === i && currentMoveLetter.col === j) {
                    currentMoveLetter = null;
                    isMoveInProgress = false;
                    //document.getElementById('reset-button').style.display = 'none';
                }
            }
            activeInput = null;
            renderBoard();
        }
    });

    cellElement.innerHTML = '';
    cellElement.appendChild(input);
    input.focus(); // Устанавливаем фокус на поле ввода
    activeInput = input; // Устанавливаем активное поле ввода

    document.getElementById('reset-button').style.display = 'block';
    document.getElementById('selection-controls').style.display = 'none'; // Скрываем кнопки выбора
}

/**
 * Проверяет, является ли клетка
 * граничущей с хотя бы одной заполненной
 */
function isAdjacentToFilled(row, col) {
    const directions = [
                  [-1,  0], 
        [ 0, -1],           [ 0,  1],
                  [ 1,  0], 
    ];
    return directions.some(([dr, dc]) => {
        const r = row + dr;
        const c = col + dc;
        return r >= 0 && r < 5 && c >= 0 && c < 5 && grid[r][c] !== '';
    });
}

/**
 * Сбросить букву
 */
function resetLetter() {
    if (currentMoveLetter) {
        grid[currentMoveLetter.row][currentMoveLetter.col] = '';
        
        currentMoveLetter = null;
        document.getElementById('reset-button').style.display = 'none';
        renderBoard();
        updateSelection();
    }
}

/**
 * Отменить выделение
 */
function cancelSelection() {
    selectedCells = [];
    updateSelection();
    document.getElementById('selection-controls').style.display = 'none';
}

/**
 * Подтвердить слово
 */
function submitWord() {
    const word = selectedCells.map(cell => grid[cell.row][cell.col]).join('');
    sendMoveToServer(word);
    document.getElementById('selection-controls').style.display = 'none';
}


/**
 * Отправляет слово на сервер для проверки
 * @param {string} word 
 */
function sendMoveToServer(word) {
    console.log(word)
    fetch('http://127.0.0.1:5000/check', {
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
    timerValue = timeForMove;
    document.getElementById('timer').textContent = `Время: ${timerValue}`;
    timerInterval = setInterval(() => {
        timerValue--;
        document.getElementById('timer').textContent = `Время: ${timerValue}`;
        if (timerValue <= 0) {
            clearInterval(timerInterval);
            //alert("Время вышло!");
            //passTurn();
        }
    }, 1000);
}


function passTurn() {
    currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
    isMoveInProgress = false;
    currentMoveLetter = null;
    document.getElementById('reset-button').style.display = 'none';
    timerValue = timeForMove;
    updateScoreboard();
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


// Инициализация игрового поля
document.addEventListener('DOMContentLoaded', () => {
    // Проверка авторизации перед началом игры
    checkAuth().then(() => {
        // Инициализация игры только после успешной авторизации
        renderBoard();
        startTimer();
        updateScoreboard();
    });
});