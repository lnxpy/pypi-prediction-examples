from datetime import datetime, timedelta

import mindsdb_sdk
import pandas as pd
import plotly.graph_objects as go

DAYS_TO_BE_PREDICTED = 100
PACKAGE_NAME = "requests"


server = mindsdb_sdk.connect()
server = mindsdb_sdk.connect("http://127.0.0.1:47334")

databases = server.list_databases()
database = databases[-1]

query = database.query(
    f'SELECT date, downloads FROM pypi_datasource.overall WHERE package="{PACKAGE_NAME}" AND mirrors=true limit 500'
)

overall_df = query.fetch()

# an empty dataframe
predicted_df = pd.DataFrame(columns=["date", "downloads"])

today = datetime.today()
current_date = (today - timedelta(days=180)).date()

for i in range(DAYS_TO_BE_PREDICTED):
    query = database.query(
        f'SELECT date, downloads FROM mindsdb.pypi_model WHERE date="{current_date}"'
    )
    predicted_value = query.fetch()
    current_date = (today + timedelta(days=i)).date()
    predicted_df = pd.concat([predicted_df, query.fetch()], ignore_index=True)


fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=overall_df["date"], y=overall_df["downloads"], mode="lines", name="Data"
    )
)
fig.add_trace(
    go.Scatter(
        x=predicted_df["date"],
        y=predicted_df["downloads"],
        mode="lines",
        name="Prediction",
    )
)
fig.update_layout(
    title="PyPI Package Download Rate Prediction",
    xaxis_title="Dates",
    yaxis_title="Downloads",
    template="plotly_dark",
)

fig.show()
