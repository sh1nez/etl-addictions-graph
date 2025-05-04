from sqlglot.expressions import (
    Insert,
    Update,
    Delete,
    Merge,
    Select,
    Expression,
    Column,
    Values,
    Alias,
)
from itertools import zip_longest
from typing import Optional, List, Tuple


def print_ifnt_str(func):  # * for testing
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, str):
            # print("!"*50)
            print("INPUT:", end=" ")
            print(*args)
            # print(args[0].args)
            print("OUTPUT:", end=" ")
            print(result)
        return result

    return wrapper


# TODO: join parse, ?Reference parse?
@print_ifnt_str
def parse_columns(op: Expression) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """If parsed correctly, returns tuple ([<source_table_column>:?<input_table_column>?],[statement_columns])."""
    try:
        if isinstance(op, Insert):
            return _parse_insert(op)
        elif isinstance(op, Update):
            return _parse_update(op)
        elif isinstance(op, Delete):
            return _parse_delete(op)
        elif isinstance(op, Merge):
            return _parse_merge(op)
        elif isinstance(op, Select):
            return _parse_select(op)
        else:
            return None
    except Exception as e:
        print(f"Error parsing column:{e}")
        return (None, None)


def _this_deep_parse(op, prior=None, typesearch=str, star_except=True) -> str:
    """Parses the element 'this' until finds str. May parse element prior if given, change required type and disable Star() class checking"""
    if isinstance(op, typesearch):
        return op
    if star_except and isinstance(op, Expression) and op.is_star:
        return "*"
    try:
        counter = 0
        while ("this" in op.args or (prior and prior in op.args)) and counter < 100:
            if prior and prior in op.args:
                op = op.args[prior]
            else:
                op = op.args["this"]
            if isinstance(op, typesearch):
                return op
            if star_except and isinstance(op, Expression) and op.is_star:
                return "*"
            counter += 1
        raise Exception("No type found")
    except Exception as e:
        print(e)
        return f"unknown"


def _where_column_names(op: Expression) -> list[str]:
    """Finding Column(s) and name(s) in where by BFS search"""
    col_names = []
    found_columns = False
    for i in Expression.bfs(op.args["where"]):
        this = i.args["this"]
        if isinstance(this, Column):
            found_columns = True
            col_names.append(_this_deep_parse(this))
        elif found_columns:
            break
    return col_names


def _parse_insert(op: Insert):
    """Returns (["<modifying_table_column>:<new_column_name>"], None) since no where in insert"""
    insert_cols = op.args["this"].args.get("expressions", ["*"])
    incoming_cols = []
    if isinstance(op.args["expression"], Values):
        incoming_cols = ["input"] * len(insert_cols)
    else:
        incoming_cols = [
            _this_deep_parse(i) for i in op.args["expression"].args["expressions"]
        ]
    return (
        [
            _this_deep_parse(i) + ":" + j
            for i, j in zip_longest(insert_cols, incoming_cols, fillvalue="*")
        ],
        None,
    )


def _parse_update(op: Update):
    """Returns (["<modifying_table_column>:<new_column_name>"], [<statement_column_name>]) if where statement exists"""
    update_cols = op.args.get("expressions", [])
    where = _where_column_names(op) if "where" in op.args and op.args["where"] else []
    if len(update_cols) != 0:
        return (
            [
                _this_deep_parse(i) + ":" + _this_deep_parse(i.args["expression"])
                for i in update_cols
            ],
            where,
        )
    raise Exception("No update columns")


def _parse_delete(op: Delete):
    """Returns (None, [<statement_column_name>]) if where statement exists"""
    if op.args["where"] is None:
        return []
    return (None, _where_column_names(op))


def _parse_merge(op: Merge):
    """Returns ([<column_name>],None) since merge op is processed separately"""
    if "on" in op.args and op.args["on"]:
        on = op.args["on"]
        return (
            [f"{_this_deep_parse(on)}:{_this_deep_parse(on, prior='expression')}"],
            None,
        )
    return ([], None)


def _select_columns(op):
    if (
        "this" in op.args
        and "this" in op.args["this"].args
        and isinstance(op.args["this"].args["this"], str)
    ):
        return op.args["this"].args["this"]
    if isinstance(op, Alias):
        return str(op.args["this"])
    return str(op)


def _parse_select(op: Select):
    """Returns ([<displaying_columns_name>], [<statement_column_name>]) if where statement exists"""
    where = []
    where = _where_column_names(op) if "where" in op.args else []
    select_cols = op.args["expressions"]
    if select_cols[0].is_star:
        return (["*"], where)
    return ([_select_columns(i) for i in select_cols], where)
