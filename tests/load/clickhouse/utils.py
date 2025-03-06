from data_load_tool.destinations.impl.clickhouse.sql_client import ClickHouseSqlClient
from data_load_tool.destinations.impl.clickhouse.typing import TDeployment


def get_deployment_type(client: ClickHouseSqlClient) -> TDeployment:
    cloud_mode = int(client.execute_sql("""
        SELECT value FROM system.settings WHERE name = 'cloud_mode'
    """)[0][0])
    return "ClickHouseCloud" if cloud_mode else "ClickHouseOSS"
