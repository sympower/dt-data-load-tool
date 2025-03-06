import data_load_tool
import humanize
import streamlit as st

from data_load_tool.common.pendulum import pendulum
from data_load_tool.helpers.streamlit_app.utils import query_data_live
from data_load_tool.helpers.streamlit_app.widgets import stat


def last_load_info(pipeline: data_load_tool.Pipeline) -> None:
    if pipeline.default_schema_name:
        loads_df = query_data_live(
            pipeline,
            f"SELECT load_id, inserted_at FROM {pipeline.default_schema.loads_table_name} WHERE"
            " status = 0 ORDER BY inserted_at DESC LIMIT 101 ",
        )

        if loads_df is None:
            st.error(
                "Load info is not available",
                icon="🚨",
            )
        else:
            loads_no = loads_df.shape[0]
            if loads_df.shape[0] > 0:
                rel_time = (
                    humanize.naturaldelta(
                        pendulum.now() - pendulum.from_timestamp(loads_df.iloc[0, 1].timestamp())
                    )
                    + " ago"
                )
                last_load_id = loads_df.iloc[0, 0]
                if loads_no > 100:
                    loads_no = "> " + str(loads_no)
            else:
                rel_time = "---"
                last_load_id = "---"

            stat("Last load time", rel_time, border_left_width=4)
            stat("Last load id", last_load_id)
            stat("Total number of loads", loads_no)
