from pympl.types import all_types
import pympl.exc as exc


def _get_table_schemas(schema):
    result = {}
    nodes = schema.element.complexType.choice.element

    if not isinstance(nodes, list):
        nodes = [nodes]

    for i in nodes:
        result[str(i._name)] = TableSchema(i)

    return result


def _normalize_type_name(type_name):
    return type_name.split(':', 1)[1]


class SchemaResolver(object):
    def __init__(self, schema, diffgram):
        self.schema = schema
        self.diffgram = diffgram
        self._check_for_error()
        self.tables = []

        schemas = _get_table_schemas(schema)

        for table_name, table_schema in schemas.iteritems():
            types = table_schema.get_types()
            try:
                rows = getattr(self.diffgram.NewDataSet, table_name)
            except AttributeError:
                continue

            result = ResultList()
            rows = rows if isinstance(rows, list) else [rows]

            for row in rows:
                parsed_row = {}
                for column_name, value in (i for i in row if i[0] in types):
                    type_ = types.get(column_name, all_types['string'])
                    parsed_row[column_name] = type_.decode(
                        value.encode('utf8'))
                result.append(parsed_row)

            setattr(self, table_name, result)
            self.tables.append(table_name)

    def _check_for_error(self):
        try:
            message = self.diffgram.NewDataSet.Table1.ErrorMessage
        except AttributeError:
            pass
        else:
            message = str(message)
            error_code, junk, error_message = message.split('|', 2)
            raise exc.ServerError(error_message.lstrip('Exception: '))


class TableSchema(object):
    def __init__(self, node):
        self.node = node

    def get_types(self):
        result = {}

        for i in self.node.complexType.sequence.element:
            type_name = _normalize_type_name(str(i._type))
            result[str(i._name)] = all_types[type_name]

        return result


class ResultList(list):
    def first(self):
        return self[0] if len(self) > 0 else None
