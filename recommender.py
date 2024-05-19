class Recommender:
    """
    Esta es la clase para hacer recomendaciones.
    La clase no debe requerir argumentos obligatorios para la inicialización.
    """

    def train(self, filename="requirements.txt") -> 'Recommender':
        """
        Permite que el recomendador aprenda qué artículos existen y cuáles han sido comprados juntos en el pasado.
        :param filename: el nombre del archivo que contiene la base de datos.
        :return: el objeto debe retornarse a sí mismo aquí (esto es realmente importante).
        """
        self.database = self.load_database(filename)

       
        self.tidsets = self.create_tidsets(self.database)

     
        self.itemsets, self.tidsets = self.eclat(self.database, 3)
        self.filtered_itemsets = self.filter_always_together(self.itemsets, self.tidsets, len(self.database))

        return self

    def load_database(self, filename):
        """
        Cargar la base de datos desde un archivo.
        :param filename: el nombre del archivo que contiene la base de datos.
        :return: una lista de listas de identificadores de artículos que se han comprado juntos.
        """
        database = []
        with open(filename, 'r') as file:
            for line in file:
                transaction = line.strip().split(',')
                database.append(transaction)
        return database

    def create_tidsets(self, transactions):
        tidsets = {}
        for tid, transaction in enumerate(transactions):
            for item in transaction:
                if item not in tidsets:
                    tidsets[item] = set()
                tidsets[item].add(tid)
        return tidsets

    def calculate_support(self, itemset, tidsets):
        return len(set.intersection(*[tidsets[item] for item in itemset]))

    def generate_candidates(self, itemsets, length):
        candidates = set()
        itemsets_list = list(itemsets)
        for i in range(len(itemsets_list)):
            for j in range(i + 1, len(itemsets_list)):
                union_set = itemsets_list[i].union(itemsets_list[j])
                if len(union_set) == length:
                    candidates.add(union_set)
        return candidates

    def eclat(self, transactions, min_support):
        tidsets = self.create_tidsets(transactions)
        itemsets = set(frozenset([item]) for item in tidsets)
        valid_itemsets = []
        k = 1
        while itemsets:
            current_itemsets = [itemset for itemset in itemsets if self.calculate_support(itemset, tidsets) >= min_support]
            valid_itemsets.extend(current_itemsets)
            k += 1
            itemsets = self.generate_candidates(set(current_itemsets), k)
        return valid_itemsets, tidsets
