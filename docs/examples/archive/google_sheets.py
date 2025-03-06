import data_load_tool

from sources.google_sheets import google_spreadsheet

data_load_tool.pipeline(destination="bigquery", dev_mode=False)
# see example.secrets.toml to where to put credentials

# "2022-05", "model_metadata"
info = google_spreadsheet(
    "11G95oVZjieRhyGqtQMQqlqpxyvWkRXowKE8CtdLtFaU", ["named range", "Second_Copy!1:2"]
)
print(list(info))
