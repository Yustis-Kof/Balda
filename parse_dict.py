import re

def restore_yo(word, pron):
    """
    Заменяет 'е' на 'ё' в слове на основе произношения.
    Удаляет символы ударений из произношения перед сравнением.
    """
    # Удаляем символы ударений
    clean_pron = re.sub(r"['`]", "", pron)
    
    # Сравниваем посимвольно только при совпадении длин
    if len(word) != len(clean_pron):
        return word
    
    restored = []
    for w_char, p_char in zip(word, clean_pron):
        if w_char == 'е' and p_char == 'ё':
            restored.append('ё')
        else:
            restored.append(w_char)
    return ''.join(restored)

def parse_dictionary(text):
    """Парсит словарь и возвращает нарицательные существительные"""
    results = []
    articles = text.strip().split('\n \n')
    
    for article in articles:
        lines = article.split('\n')
        if not lines:
            continue
            
        # Обрабатываем только леммы (первые строки статей)
        lemma_line = lines[0]
        fields = lemma_line.split(' | ')
        num_fields = len(fields)
        
        # Пропускаем некорректные записи
        if num_fields not in (4, 7):
            continue
            
        # Извлекаем поля в зависимости от формата
        if num_fields == 7:
            word, morph, pron, freq_str, prop, sem, code = fields
        else:  # 4 поля
            word, morph, pron, code = fields
            freq_str, prop = '0', ''
        
        # Проверяем, что это нарицательное существительное
        if 'сущ' not in morph.split() or prop.strip():
            continue
            
        # Восстанавливаем букву "ё"
        restored_word = restore_yo(word, pron)
        
        # Обрабатываем частотность
        try:
            frequency = float(freq_str) if freq_str.strip() else 0.0
        except ValueError:
            frequency = 0.0
            
        results.append(restored_word)
        
    return results

if __name__ == "__main__":
    with open('dictionary.txt', 'r', encoding='utf-8') as f:
        dictionary_text = f.read()
    
    nouns_list = parse_dictionary(dictionary_text)
    
    open("nouns.txt", "w", encoding="utf-8").write('\n'.join(nouns_list))