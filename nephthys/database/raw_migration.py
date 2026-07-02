from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


# Dummy table we use to execute raw SQL with
class RawTable(Table):
    pass


def split_sql_statements(sql: str) -> list[str]:
    """
    Split SQL into statements on semicolons, but ignore semicolons inside
    dollar-quoted blocks ($$...$$ or $tag$...$tag$) and quoted strings.
    """
    statements: list[str] = []
    buf: list[str] = []

    i = 0
    n = len(sql)

    in_single = False
    in_double = False
    dollar_tag: str | None = None

    while i < n:
        ch = sql[i]

        # Handle dollar-quoted blocks: $tag$ ... $tag$
        if not in_single and not in_double:
            if dollar_tag is None and ch == "$":
                j = i + 1
                while j < n and (sql[j].isalnum() or sql[j] == "_"):
                    j += 1
                if j < n and sql[j] == "$":
                    dollar_tag = sql[i : j + 1]
                    buf.append(dollar_tag)
                    i = j + 1
                    continue
            elif dollar_tag is not None and sql.startswith(dollar_tag, i):
                buf.append(dollar_tag)
                i += len(dollar_tag)
                dollar_tag = None
                continue

        if dollar_tag is None:
            # Toggle single-quoted string
            if not in_double and ch == "'":
                if in_single and i + 1 < n and sql[i + 1] == "'":
                    # Escaped single quote inside string
                    buf.append("''")
                    i += 2
                    continue
                in_single = not in_single
                buf.append(ch)
                i += 1
                continue

            # Toggle double-quoted identifier
            if not in_single and ch == '"':
                in_double = not in_double
                buf.append(ch)
                i += 1
                continue

            # Split point
            if not in_single and not in_double and ch == ";":
                stmt = "".join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
                i += 1
                continue

        buf.append(ch)
        i += 1

    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)

    return statements


def raw_migration(
    migration_id: str,
    app_name: str,
    description: str,
    forwards: str,
    backwards: str | None = None,
):
    manager = MigrationManager(
        migration_id=migration_id, app_name=app_name, description=description
    )

    async def run():
        for statement in split_sql_statements(forwards):
            await RawTable.raw(statement)

    manager.add_raw(run)

    if backwards:

        async def run_backwards():
            for statement in split_sql_statements(backwards):
                await RawTable.raw(statement)

        manager.add_raw_backwards(run_backwards)

    return manager
