class Tabletype:
    def __init__(self,name,dependence_type):
        self.name = name
        self.type =dependence_type
        self.dependencies = []
    def add_dependencies(self, target:"Tabletype",relation:str):
        self.dependencies.append((target,relation))
    def __repr__(self):
        return f'Tabletype ({self.name},{self.type})'

# Создание узлов (таблиц и CTE)
orders = Tabletype("orders", "table")  # Обычная таблица в базе данных
tmp = Tabletype("tmp", "cte")  # Временная CTE (Common Table Expression)
vip_users = Tabletype("vip_users", "table")  # Другая таблица

# Установка зависимостей
orders.add_dependencies(tmp, "read")  # Таблица "orders" читает данные из CTE "tmp"
tmp.add_dependencies(vip_users, "insert")  # CTE "tmp" вставляет данные в "vip_users"

# Проверка зависимостей
for node in [orders, tmp, vip_users]:
    print(f"Узел: {node.name} ({node.type})")
    for dep, rel in node.dependencies:
        print(f"  → {dep.name} ({rel})")
