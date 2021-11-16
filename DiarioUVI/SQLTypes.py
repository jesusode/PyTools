#Tabla de conversion SQL <-> Python

import datetime
import decimal

SQLTYPES_TABLE= {
    "BIT": bool,
    "TINYINT": int,
    "SMALLINT": int,
    "INTEGER": int,
    "BIGINT": int,
    "REAL": float,
    "DOUBLE": float,
    "DECIMAL": decimal.Decimal,
    "NUMERIC": int,
    "CHAR": str,
    "VARCHAR": str,
    "LONGVARCHAR": str,
    "TEXT": str,
    "DATE": datetime.date,
    "TIME": datetime.time,
    "TIMESTAMP": datetime.datetime,
    "BINARY": bytes,
    "VARBINARY": bytes,
    "LONGVARBINARY": bytes,
    "BLOB": bytes,
    "CLOB": bytes,
    "ARRAY": bytes,
    "REF": int,
    "STRUCT": dict #?
}

PY2SQL_TABLE={
    "bool" : "BIT",
    "int" : "INTEGER",
    "float" : "DOUBLE",
    "decimal.Decimal" : "DECIMAL",
    "str" : "VARCHAR",
    "datetime.Date" : "DATE",
    "datetime.Time" : "TIME",
    "datetime.Datetime" : "TIMESTAMP",
    "bytes" : "BLOB",
    "dict" : "STRUCT" 
}