import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from utils import Header, make_dash_table
import pandas as pd
import pathlib

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()


df_graph = pd.read_csv(DATA_PATH.joinpath("df_actual_vs_budget.csv"))


def create_layout(app):
    return html.Div(
        [
            Header(app),
            # page 2
            html.Div(
                [
                    # Row
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Actual vs Budget", className="subtitle padded"),
                                    dcc.Graph(
                                        id="graph-1",
                                        figure={
                                            "data": [
                                                go.Scatter(
                                                    x=df_graph["Quarter"],
                                                    y=df_graph["Budget"],
                                                    line={"color": "#97151c"},
                                                    mode="lines",
                                                    name="Actual",
                                                ),
                                                go.Bar(
                                                    x=df_graph["Quarter"],
                                                    y=df_graph["Actual"],
                                                    line={"color": "#b5b5b5"},
                                                    mode="bar",
                                                    name="Budget",
                                                ),
                                            ],
                                            "layout": go.Layout(
                                                autosize=True,
                                                width=700,
                                                height=200,
                                                font={"family": "Raleway", "size": 10},
                                                margin={
                                                    "r": 30,
                                                    "t": 30,
                                                    "b": 30,
                                                    "l": 30,
                                                },
                                                showlegend=True,
                                                titlefont={
                                                    "family": "Raleway",
                                                    "size": 10,
                                                },
                                                xaxis={
                                                    "autorange": True,
                                                    "showline": True,
                                                    "type": "date",
                                                    "zeroline": False,
                                                },
                                                yaxis={
                                                    "autorange": True,
                                                    "showline": True,
                                                    "type": "linear",
                                                    "zeroline": False,
                                                },
                                            ),
                                        },
                                        config={"displayModeBar": False},
                                    ),
                                ],
                                className="six columns",
                            ),
                        ],
                        className="row ",
                    ),
                    # Row 2
                    # Row 3
                    # Row 4
                    # Row 5
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )