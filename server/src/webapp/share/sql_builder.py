# -*- coding:utf-8 -*-


class SqlBuilder(object):
    """Sql builder基类
    """

    def __init__(self, table_name, kvs=None, cond=None):
        self._table_name = table_name
        self._kvs = kvs
        self._cond = cond

    def build(self):
        raise NotImplementedError()


class InsertBuilder(SqlBuilder):
    """insert builder
    """

    def __init__(self, table_name, kvs=None, cond=None, ignore=False):
        super().__init__(table_name, kvs, cond)
        self._ignore = ignore

    def build(self):
        args = []
        keys = []
        for k, v in self._kvs.items():
            if k is None or v is None:
                continue
            keys.append(k)
            args.append(v)
        link_keys = "`,`".join(keys)
        link_values = ",".join(["%s"] * len(args))
        sql = f"INSERT {'IGNORE' if self._ignore else ''} INTO %s (`%s`) VALUES (%s)" % (
        self._table_name, link_keys, link_values)
        return sql, args


class ReplaceBuilder(SqlBuilder):
    """insert builder
    """

    def __init__(self, table_name, kvs=None, cond=None):
        super().__init__(table_name, kvs, cond)

    def build(self):
        args = []
        keys = []
        for k, v in self._kvs.items():
            if k is None or v is None:
                continue
            keys.append(k)
            args.append(v)
        link_keys = "`,`".join(keys)
        link_values = ",".join(["%s"] * len(args))
        sql = "REPLACE INTO %s (`%s`) VALUES (%s)" % (self._table_name, link_keys, link_values)
        return sql, args


class UpdateBuilder(SqlBuilder):
    """update builder
    """

    def __init__(self, table_name, kvs=None, cond=None):
        super().__init__(table_name, kvs, cond)

    def build(self):
        kvs = []
        args = []
        for k, v in self._kvs.items():
            if v is None:
                continue
            kvs.append("{0}=%s".format(k))
            args.append(v)
        link_kvs = ", ".join(kvs)
        if not link_kvs:
            return "", []
        sql = "UPDATE %s SET %s" % (self._table_name, link_kvs)
        if self._cond:
            conditions, sub_args = self._cond.build()
            sql = "%s WHERE %s" % (sql, conditions)
            args += sub_args
        return sql, args


class DeleteBuilder(SqlBuilder):
    """remove builder
    """

    def __init__(self, table_name, kvs=None, cond=None):
        super().__init__(table_name, kvs, cond)

    def build(self):
        sql = "DELETE FROM %s" % self._table_name
        args = []
        if self._cond:
            conditions, sub_args = self._cond.build()
            sql = "%s WHERE %s" % (sql, conditions)
            args += sub_args
        return sql, args


class TotalBuilder(SqlBuilder):
    """
    """
    def __init__(self, table_name, cond=None):
        super().__init__(table_name, cond=cond)

    def build(self):
        sql = "SELECT COUNT(1) as total FROM %s" % self._table_name
        args = []
        if self._cond:
            conditions, sub_args = self._cond.build()
            sql = "%s WHERE %s" % (sql, conditions)
            args += sub_args
        return sql, args


class PageBuilder(SqlBuilder):
    """
    """
    def __init__(self, table_name, columns, start, limit=None, orderby=None, desc=False, cond=None):
        self._start = start
        self._limit = limit
        self._columns = columns
        self._orderby = orderby
        self._desc = desc
        super().__init__(table_name, cond=cond)

    def build(self):
        link_columns = ",".join(self._columns)
        sql = "SELECT %s FROM %s" % (link_columns, self._table_name)
        args = []
        if self._cond:
            conditions, sub_args = self._cond.build()
            sql = f"{sql} WHERE {conditions}"
            args += sub_args
        if self._orderby:
            sql = f"{sql} ORDER BY {self._orderby}"
            if self._desc:
                sql = f"{sql} DESC"
        if self._start or self._limit:
            if self._limit:
                sql = f"{sql} LIMIT %s, %s"
                args += (self._start, self._limit)
            else:
                sql = f"{sql} LIMIT %s"
                args += (self._start,)
        return sql, args


class SelectBuilder(SqlBuilder):
    """
    """
    def __init__(self, table_name, columns=None, orderby=None, desc=False, cond=None):
        self._columns = columns if columns else ["*"]
        self._orderby = orderby
        self._desc = desc
        super().__init__(table_name, cond=cond)

    def build(self):
        link_columns = ",".join(self._columns)
        sql = "SELECT %s FROM %s" % (link_columns, self._table_name)
        args = []
        if self._cond:
            conditions, sub_args = self._cond.build()
            sql = f"{sql} WHERE {conditions}"
            args += sub_args
        if self._orderby:
            sql = f"{sql} ORDER BY {self._orderby}"
            if self._desc:
                sql = f"{sql} DESC"
        return sql, args


class SqlConditionBuilder(object):
    """sql条件构建者
    """

    def __init__(self, *conds):
        self._conds = conds
        self._link = None

    def _build_for_dict(self, dic):
        if not self._link:
            raise NotImplementedError()
        if not isinstance(dic, dict):
            raise ValueError("condition invalid, cond: %s" % dic)
        parts = []
        args = []
        for k, v in dic.items():
            if k is None or v is None:
                continue
            if isinstance(v, tuple) or isinstance(v, list):
                # value是tuple或list 构造IN结构
                parts.append("{0} IN ({1})".format(k, ", ".join(["%s"] * len(v))))
                for item in v:
                    args.append(item)
                continue
            if isinstance(v, SQL_CONDITION_EXPRESSION):
                sub_sql, sub_args = v.build(k)
                parts.append("%s" % sub_sql)
                args += sub_args
                continue
            parts.append("{0}=%s".format(k))
            args.append(v)
        if len(parts) == 0:
            return '(1=1)', []
        return self._link.join(parts), args

    def build(self):
        if not self._link:
            raise NotImplementedError()
        parts = []
        args = []
        for cond in self._conds:
            if not cond:
                continue
            if isinstance(cond, dict):
                sub_sql, sub_args = self._build_for_dict(cond)
                parts.append("(%s)" % sub_sql)
                args += sub_args
                continue
            if isinstance(cond, SqlConditionBuilder):
                sub_sql, sub_args = cond.build()
                parts.append("(%s)" % sub_sql)
                args += sub_args
                continue
            raise ValueError("condition invalid, cond: %s" % cond)
        if len(parts) == 0 or (len(parts) == 1 and parts[0] == '()'):
            return '(1)', []
        return self._link.join(parts), args


class SqlAND(SqlConditionBuilder):
    def __init__(self, *conds):
        super().__init__(*conds)
        self._link = " AND "


class SqlOR(SqlConditionBuilder):
    def __init__(self, *conds):
        super().__init__(*conds)
        self._link = " OR "


class SQL_CONDITION_EXPRESSION(object):
    """SQL条件表达式抽象类
    """

    def build(self, key):
        raise NotImplementedError("Abstract class not implements the methods")


class SQL_NOT_IN(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise RuntimeError("value should be list or tuple")
        self._value = value

    def build(self, key):
        if not self._value:
            sql = '1=1'
            args = []
        else:
            sql = f'{key} NOT IN ({",".join(["%s"] * len(self._value))})'
            args = self._value
        return sql, args


class SQL_IN(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise RuntimeError("value should be list or tuple")
        self._value = value

    def build(self, key):
        if not self._value:
            sql = '1=1'
            args = []
        else:
            sql = f'{key} IN ({",".join(["%s"] * len(self._value))})'
            args = self._value
        return sql, args


class SQL_GT(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0}>%s".format(key)
        args = [self._value]
        return sql, args


class SQL_EGT(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0}>=%s".format(key)
        args = [self._value]
        return sql, args


class SQL_LT(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0}<%s".format(key)
        args = [self._value]
        return sql, args


class SQL_ELT(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0}<=%s".format(key)
        args = [self._value]
        return sql, args


class SQL_INTERVAL(SQL_CONDITION_EXPRESSION):
    def __init__(self, first, second):
        self._first = first
        self._second = second

    def build(self, key):
        sql = "{0}>%s AND {0}<%s".format(key, key)
        args = [self._first, self._second]
        return sql, args


class SQL_CLOSE_INTERVAL(SQL_CONDITION_EXPRESSION):
    def __init__(self, first, second):
        self._first = first
        self._second = second

    def build(self, key):
        sql = "{0}>=%s AND {0}<=%s".format(key, key)
        args = [self._first, self._second]
        return sql, args


class SQL_LIKE(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0} LIKE %s".format(key)
        args = [self._value]
        return sql, args


class SQL_REGEXP(SQL_CONDITION_EXPRESSION):
    def __init__(self, value):
        self._value = value

    def build(self, key):
        sql = "{0} REGEXP %s".format(key)
        args = [self._value]
        return sql, args


def build(start, limit, *, category_id, author, keyword, title, posted):
    conds = []
    cond = {}
    conds.append(cond)
    table = ['articles']
    join_partes = []
    if category_id:
        table.append('article_category_mapper')
        cond['article_category_mapper.category_id'] = category_id
        join_partes.append('articles.article_id = article_category_mapper.article_id')
    if keyword:
        table.append('users')
        conds.append(SqlOR({
            'users.nickname': SQL_LIKE(f'%{keyword}%'),
            'articles.title': SQL_LIKE(f'%{keyword}%')
        }))
        join_partes.append('articles.author = users.uid')
    if title:
        cond['aritlces.title'] = SQL_LIKE(f'%{title}%')
    cond.update({
        'author': author,
        'posted': posted
    })
    clause, clause_args = SqlAND(*conds).build()
    print(clause, clause_args)


if __name__ == "__main__":
    cond1 = SqlAND({'a.test': SQL_LIKE('fuck')})
    sql1, args1 = cond1.build()
    print("sql1: %s" % sql1)
    print("args1: %s" % args1)
    sql2, args2 = DeleteBuilder("users", cond=SqlAND({"a": [1, 2]})).build()
    print("sql2: %s" % sql2)
    print("args2: %s" % args2)
    sql3, args3 = InsertBuilder("users", kvs={"name": "lsj", "age": 10}).build()
    print("sql3: %s" % sql3)
    print("args3: %s" % args3)
    sql4, args4 = UpdateBuilder("users", kvs={"name": "xxx", "age": 10}, cond=SqlAND({"name": "lsj"})).build()
    print("sql4: %s" % sql4)
    print("args4: %s" % args4)
