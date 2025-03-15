const board = document.getElementById('board');
// Пример игрового поля
const grid = [
    ['', '', '', '', ''],
    ['', '', '', '', ''],
    ['Б', 'А', 'Л', 'Д', 'А'],
    ['', '', '', '', ''],
    ['', '', '', '', '']
];

let isSelecting = false; // Флаг для отслеживания процесса выбора
let selectedCells = []; // Массив для хранения выбранных клеток

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
    if ((rowDiff <= 1 && colDiff <= 1) && !(rowDiff === 0 && colDiff === 0)) {
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

    // Получаем слово из выбранных клеток
    const word = selectedCells.map(cell => grid[cell.row][cell.col]).join('');
    if(word.length > 1){
        console.log('Выбранное слово:', word);

        // Отправляем слово на сервер
        sendMoveToServer(word);
    }
    // Сбрасываем выделение
    selectedCells = [];
    updateSelection();
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
}

let activeInput = null; // Глобальная переменная для отслеживания активного поля ввода

/**
 * Создаёт в указанной клетке текстовое поле длиной
 * в 1 символ, которое удаляется при потере фокуса
 * @param {number} i 
 * @param {number} j 
 */
function addLetter(i, j) {
    if (grid[i][j] !== '') {
        return; // Если клетка уже занята, ничего не делаем
    }

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
            grid[i][j] = value; // Обновляем значение в сетке
        } else {
            grid[i][j] = "";
        }
        activeInput = null; // Сбрасываем активное поле ввода
        renderBoard();
    });

    // При нажатии Enter сохраняем букву в клетке
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const value = e.target.value.toUpperCase();
            if (value) {
                grid[i][j] = value; // Обновляем значение в сетке
            } else {
                grid[i][j] = "";
            }
            activeInput = null; // Сбрасываем активное поле ввода
            renderBoard();
        }
    });

    cellElement.innerHTML = '';
    cellElement.appendChild(input);
    input.focus(); // Устанавливаем фокус на поле ввода
    activeInput = input; // Устанавливаем активное поле ввода
}

/**
 * Отправляет слово на сервер для проверки
 * @param {string} word 
 */
function sendMoveToServer(word) {
    fetch('http://127.0.0.1:5000/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ word: word })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Ошибка:', error));
}

// Инициализация игрового поля
renderBoard();