from app.database import get_db_connection

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



word_trie = Trie()

def load_dictionary():
    global word_trie
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT word FROM dictionary"
            cursor.execute(sql)
            result = cursor.fetchall()

            # Загружаем все слова в префиксное дерево
            for row in result:
                word_trie.insert(row['word'].lower())
    finally:
        connection.close()

def check_word(word):
    return word_trie.search(word)