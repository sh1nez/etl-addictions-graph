Взаимодействие компонентов
----------------------------

----------------
Схема выполнения
----------------
.. graphviz::
    :align: center
    :caption: Схема выполнения

    digraph workflow {
        rankdir=LR;
        main -> cli [label="Парсинг аргументов"];
        main -> logger_config [label="Инициализация логгера"];
        main -> "table/run" [label="--mode table"];
        main -> "field/run" [label="--mode field"];
        main -> "func/run" [label="--mode functional"];
    }
