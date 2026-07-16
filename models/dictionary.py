import sqlite3

class TrieNode:
    """Узел префиксного дерева"""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    """Префиксное дерево
    
    По сути это дерево, содержащее все слова"""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Вставить слово в префиксное дерево

        :param word: Слово"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """Найти слово в префиксном дереве
        
        :param word: Слово"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word
    
    def search_prefix(self, prefix):
        """Найти префикс или слово в префиксном дереве
        
        :param prefix: Префикс"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True



class Dictionary:
    """Словарь"""
    def __init__(self):
        self.word_trie = Trie()

    def load_dictionary(self, dictionary="dictionary", pos=["сущ"], min_freq=0, max_freq=1000000, min_length=1, max_length=100):
        """Загрузить словарь из БД"""
        if isinstance(pos, str):
            pos = [pos]

        connection = sqlite3.connect("balda.db")
        try:
            cursor = connection.cursor()
            placeholders = ", ".join("?" for _ in pos)
            sql = f"SELECT word FROM dictionary WHERE freq BETWEEN ? AND ? AND LENGTH(word)*2 BETWEEN ? AND ? AND pos IN ({placeholders})"
            cursor.execute(sql, (min_freq, max_freq, min_length, max_length, *pos))
            result = cursor.fetchall()

            # Загружаем все слова в префиксное дерево
            for row in result:
                self.word_trie.insert(row[0].lower())
            cursor.close()
        finally:
            connection.close()

    def check_word(self, word):
        """Проверить, есть ли слово в словаре"""
        return self.word_trie.search(word)

    def check_prefix(self, prefix):
        """Проверить, есть ли префикс в словаре"""
        return self.word_trie.search_prefix(prefix)