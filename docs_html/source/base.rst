Базовые модули
==================================

Описание базовых классов

**Взаимодействие компонентов**

Парсинг:
  DirectoryParser → SqlAst → Извлечение зависимостей → GraphStorage.

Хранение:
  GraphStorage сохраняет зависимости → Передаёт данные в GraphVisualizer.

Визуализация:
    GraphVisualizer строит граф → Сохраняет/отображает результат.

Управление:
 GraphManager объединяет все этапы → Запускается через run.py.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   manager
   parser
   run
   storage
   visualize
