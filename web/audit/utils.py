from django.db import connection


def enable_audit_for_table(table_name: str) -> None:
    """
    Aktywuje trigger audytowy dla wskazanej tabeli w PostgreSQL.
    Wymaga, aby tabela posiadała kolumnę 'id'.
    """
    sql = f"""
    DROP TRIGGER IF EXISTS audit_trigger ON {table_name};
    CREATE TRIGGER audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON {table_name}
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)

def disable_audit_for_table(table_name: str) -> None:
    """
    Usuwa trigger audytowy z wybranej tabeli.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TRIGGER IF EXISTS audit_trigger ON {table_name};")