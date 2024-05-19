class Recommender:
    def train(self, prices, database_file) -> 'Recommender':
        self.database = self.load_database(database_file)
        num_items = self.get_num_items(self.database)
        self.prices = prices if prices else list(range(num_items))
        self.tidsets = self.create_tidsets(self.database)
        self.itemsets, self.tidsets = self.eclat(self.database, 3)
        self.filtered_itemsets = self.filter_always_together(self.itemsets, self.tidsets, len(self.database))
        return self

    def load_database(self, filename):
        database = []
        with open(filename, 'r') as file:
            for line in file:
                items = line.strip().split(',')
                database.append(items)
        return database

    def get_num_items(self, database):
        items = set()
        for transaction in database:
            items.update(transaction)
        return len(items)

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

    def filter_always_together(self, itemsets, tidsets, total_transactions):
        return [itemset for itemset in itemsets if self.calculate_support(itemset, tidsets) != total_transactions]

    def calculate_metrics(self, itemset, tidsets, total_transactions):
        support_itemset = self.calculate_support(itemset, tidsets)
        support = support_itemset / total_transactions

        item_supports = {item: len(tidsets[item]) / total_transactions for item in itemset}

        metrics = {
            'support': support,
            'confidence': {},
            'lift': {},
            'leverage': {},
            'odds_ratio': {}
        }

        for item in itemset:
            confidence = support / item_supports[item] if item_supports[item] != 0 else 0
            metrics['confidence'][item] = confidence

        for a in itemset:
            for b in itemset:
                if a != b:
                    support_a = item_supports[a]
                    support_b = item_supports[b]
                    lift = support / (support_a * support_b) if (support_a * support_b) != 0 else 0
                    leverage = support - (support_a * support_b)
                    odds_ratio = (support * (1 - support_a) * (1 - support_b)) / ((support_a - support) * (support_b - support)) if (support_a - support) * (support_b - support) != 0 else 0

                    metrics['lift'][(a, b)] = lift
                    metrics['leverage'][(a, b)] = leverage
                    metrics['odds_ratio'][(a, b)] = odds_ratio

        return metrics

    def get_top_recommendations(self, itemsets, tidsets, total_transactions):
        recommendations = {}
        for itemset in itemsets:
            metrics = self.calculate_metrics(itemset, tidsets, total_transactions)
            for item in itemset:
                if item not in recommendations:
                    recommendations[item] = []
                for other_item in itemset:
                    if item != other_item:
                        score = metrics['lift'].get((item, other_item), 0)
                        recommendations[item].append((other_item, score))

        for item in recommendations:
            seen = set()
            unique_recs = []
            for other_item, score in recommendations[item]:
                if other_item not in seen:
                    unique_recs.append((other_item, score))
                    seen.add(other_item)
            recommendations[item] = sorted(unique_recs, key=lambda x: x[1], reverse=True)[:3]

        return recommendations

    def get_recommendations(self, cart: list, max_recommendations: int) -> list:
        recommendations = self.get_top_recommendations(self.filtered_itemsets, self.tidsets, len(self.database))

        recommended_items = set()
        for item in cart:
            if item in recommendations:
                for rec_item, _ in recommendations[item]:
                    if rec_item not in cart and rec_item not in recommended_items:
                        recommended_items.add(rec_item)
                        if len(recommended_items) >= max_recommendations:
                            break
            if len(recommended_items) >= max_recommendations:
                break

        return list(recommended_items)

database_file = 'requirements.txt'
prices = list(range(10))  # Ejemplo de lista de precios, puede ser personalizada según necesidad
recommender = Recommender().train(prices, database_file)
recommendations = recommender.get_top_recommendations(recommender.filtered_itemsets, recommender.tidsets, len(recommender.database))

for item, recs in recommendations.items():
    rec_items = ', '.join([rec[0] for rec in recs])
    print(f"Item: {item}")
    print(f"  Recommend: {rec_items}")
