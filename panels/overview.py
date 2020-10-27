# -*- coding: utf-8 -*-
from datetime import date
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go

from app import app, indicator, millify, df_to_table, sf_manager

def currentMonth():
    today = date.today()
    return today.year * 100 + today.month

def actual_vs_budget(mu, product, df):
#    df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")

    # source filtering
    if product != "all_s":
        df = df[df["Product"] == product]

    # period filtering
    if mu != "ALL":
        df = df[df["Market Unit"] == mu]

    df = df[df["Account"] == 'Revenue']

    df = (
        df.groupby([pd.Grouper(key="Quarter")])
        .sum()
        .reset_index()
        .sort_values("Quarter")
    )

    # if no results were found
    if df.empty:
        layout = dict(
            autosize=True, annotations=[dict(text="No results found", showarrow=False)]
        )
        return {"data": [], "layout": layout}

    trace = go.Bar(
        x=df["Quarter"],
        y=df["Amount"],
        name="Actual",
    )

    trace1 = go.Scatter(
        x=df["Quarter"],
        y=df["Forecast"],
        name="Forecast",
    )
    
    data = [trace, trace1]

    layout = go.Layout(
        autosize=True,
        xaxis=dict(showgrid=False),
        margin=dict(l=35, r=5, b=80, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
                 orientation="h",
                 yanchor="bottom",
                 y=1.02,
                 xanchor="right",
                 x=1
        )        
    )

    return {"data": data, "layout": layout}

def finance_indicator(mu, product, df, account):
    # source filtering
    if product != "all_s":
        df = df[df["Product"] == product]

    # period filtering
    if mu != "ALL":
        df = df[df["Market Unit"] == mu]

    df = df[df["Account"] == account]

    df = (
        df.groupby([pd.Grouper(key="Month")])
        .sum()
        .reset_index()
        .sort_values("Month")
    )

    # if no results were found
    if df.empty:
        layout = dict(
            autosize=True, annotations=[dict(text="No results found", showarrow=False)]
        )
        return {"data": [], "layout": layout}

    won = millify(str(df[df["Month"] == currentMonth()]["Amount"].sum()))
    return won

# returns heat map figure
def heat_map_fig(df, x, y):
    z = []
    for lead_type in y:
        z_row = []
        for stage in x:
            probability = df[(df["StageName"] == stage) & (df["Type"] == lead_type)][
                "Probability"
            ].mean()
            z_row.append(probability)
        z.append(z_row)

    trace = dict(
        type="heatmap", z=z, x=x, y=y, name="mean probability", colorscale="Blues"
    )
    layout = dict(
        autosize=True,
        margin=dict(t=25, l=210, b=85, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return go.Figure(data=[trace], layout=layout)


# returns top 5 open opportunities
def top_open_opportunities(df):
    df = df.sort_values("Amount", ascending=True)
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].iloc[:5]
    # only display 21 characters
    df["Name"] = df["Name"].apply(lambda x: x[:30])
    return df_to_table(df)


# returns top 5 lost opportunities
def top_lost_opportunities(df):
    df = df[df["StageName"] == "Closed Lost"]
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].sort_values("Amount", ascending=False).iloc[:5]
    # only display 21 characters
    df["Name"] = df["Name"].apply(lambda x: x[:30])
    return df_to_table(df)


# returns modal (hidden by default)
def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "New Opportunity",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="opportunities_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            ["Name"],
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_name",
                                            placeholder="Name of the opportunity",
                                            type="text",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            ["StageName"],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_stage",
                                            options=[
                                                {
                                                    "label": "Prospecting",
                                                    "value": "Prospecting",
                                                },
                                                {
                                                    "label": "Qualification",
                                                    "value": "Qualification",
                                                },
                                                {
                                                    "label": "Needs Analysis",
                                                    "value": "Needs Analysis",
                                                },
                                                {
                                                    "label": "Value Proposition",
                                                    "value": "Value Proposition",
                                                },
                                                {
                                                    "label": "Id. Decision Makers",
                                                    "value": "Closed",
                                                },
                                                {
                                                    "label": "Perception Analysis",
                                                    "value": "Perception Analysis",
                                                },
                                                {
                                                    "label": "Proposal/Price Quote",
                                                    "value": "Proposal/Price Quote",
                                                },
                                                {
                                                    "label": "Negotiation/Review",
                                                    "value": "Negotiation/Review",
                                                },
                                                {
                                                    "label": "Closed/Won",
                                                    "value": "Closed Won",
                                                },
                                                {
                                                    "label": "Closed/Lost",
                                                    "value": "Closed Lost",
                                                },
                                            ],
                                            clearable=False,
                                            value="Prospecting",
                                        ),
                                        html.P(
                                            "Source",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_source",
                                            options=[
                                                {"label": "Web", "value": "Web"},
                                                {
                                                    "label": "Phone Inquiry",
                                                    "value": "Phone Inquiry",
                                                },
                                                {
                                                    "label": "Partner Referral",
                                                    "value": "Partner Referral",
                                                },
                                                {
                                                    "label": "Purchased List",
                                                    "value": "Purchased List",
                                                },
                                                {"label": "Other", "value": "Other"},
                                            ],
                                            value="Web",
                                        ),
                                        html.P(
                                            ["Close Date"],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        html.Div(
                                            dcc.DatePickerSingle(
                                                id="new_opportunity_date",
                                                min_date_allowed=date.today(),
                                                # max_date_allowed=dt(2017, 9, 19),
                                                initial_visible_month=date.today(),
                                                date=date.today(),
                                            ),
                                            style={"textAlign": "left"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Type",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_type",
                                            options=[
                                                {
                                                    "label": "Existing Customer - Replacement",
                                                    "value": "Existing Customer - Replacement",
                                                },
                                                {
                                                    "label": "New Customer",
                                                    "value": "New Customer",
                                                },
                                                {
                                                    "label": "Existing Customer - Upgrade",
                                                    "value": "Existing Customer - Upgrade",
                                                },
                                                {
                                                    "label": "Existing Customer - Downgrade",
                                                    "value": "Existing Customer - Downgrade",
                                                },
                                            ],
                                            value="New Customer",
                                        ),
                                        html.P(
                                            "Amount",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_amount",
                                            placeholder="0",
                                            type="number",
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                        html.P(
                                            "Probability",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_probability",
                                            placeholder="0",
                                            type="number",
                                            max=100,
                                            step=1,
                                            value="",
                                            style={"width": "100%"},
                                        ),
                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15"},
                                ),
                            ],
                            className="row",
                            style={"paddingTop": "2%"},
                        ),
                        html.Span(
                            "Submit",
                            id="submit_new_opportunity",
                            n_clicks=0,
                            className="button button--primary add pretty_container",
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="opportunities_modal",
        style={"display": "none"},
    )


layout = [
    html.Div(
        id="overview_grid",
        children=[
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="market_unit_dropdown",
                    options=[
                        {"label": "All Market Units", "value": "ALL"},
                        {"label": "US", "value": "US"},
                        {"label": "Canada", "value": "CANADA"},
                        {"label": "UK and Ireland", "value": "UKI"},
                        {"label": "Germany", "value": "GERMANY"},
                        {"label": "France", "value": "FRANCE"},
                        {"label": "Japan", "value": "JAPAN"},
                        {"label": "Singapore", "value": "SINGAPORE"},
                        {"label": "Hong Kong", "value": "HONGKONG"},
                    ],
                    value="ALL",
                    clearable=False,
                ),
            ),
            html.Div(
                className="control dropdown-styles",
                children=dcc.Dropdown(
                    id="product_dropdown",
                    options=[
                        {"label": "All Products", "value": "all_s"},
                        {"label": "Enterprise Suite", "value": "suite"},
                        {"label": "Services", "value": "services"},
                        {"label": "Other", "value": "other"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
            ),
            html.Div(
                id="overview_indicators",
                className="row indicators",
                children=[
                    indicator(
                        "#00cc96", "Forecasted Revenue this Month", "left_finance_indicator"
                    ),
                    indicator(
                        "#119DFF",
                        "Net Income this Month",
                        "middle_finance_indicator",
                    ),
                    indicator(
                        "#EF553B", "New Customer this Month", "right_overview_indicator"
                    ),
                ],
            ),
            html.Div(
                id="actual_vs_budget_container",
                className="row chart_div pretty_container",
                children=[
                    html.P("Actual vs Forecast"),
                    dcc.Graph(
                        id="actual_vs_budget",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="sales_pipeline_container",
                className="chart_div pretty_container",
                children=[
                    html.P("Sales Pipeline"),
                    dcc.Graph(
                        id="sales_pipeline",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="customer_churn_container",
                className="chart_div pretty_container",
                children=[
                    html.P("Customer Churn"),
                    dcc.Graph(
                        id="customer_churn",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
            ),
            html.Div(
                id="top_open_container",
                className="pretty_container",
                children=[
                    html.Div([html.P("Income Statement")], className="subtitle"),
                    html.Div(id="top_open_opportunities", className="table"),
                ],
            ),
        ],
    ),
    modal(),
]


# updates heatmap figure based on dropdowns values or df updates
@app.callback(
    Output("actual_vs_budget", "figure"),
    [
        Input("market_unit_dropdown", "value"),
        Input("product_dropdown", "value"),
        Input("finance_df", "data"),
    ],
)
def actual_vs_budget_callback(market_unit, product, df):
    df = pd.read_csv(df)
    return actual_vs_budget(market_unit, product, df)

@app.callback(
    Output("left_finance_indicator", "children"),
    [
        Input("market_unit_dropdown", "value"),
        Input("product_dropdown", "value"),
        Input("finance_df", "data"),
    ],
)
def left_finance_indicator_callback(market_unit, product, df):
    df = pd.read_csv(df)
    val = finance_indicator(market_unit, product, df, "Revenue")
    return dcc.Markdown("**{}**".format(val))
    
@app.callback(
    Output("middle_finance_indicator", "children"),
    [
        Input("market_unit_dropdown", "value"),
        Input("product_dropdown", "value"),
        Input("finance_df", "data"),
    ],
)
def indicator2_callback(market_unit, product, df):
    df = pd.read_csv(df)
    val = finance_indicator(market_unit, product, df, "Net Income")
    return dcc.Markdown("**{}**".format(val))

@app.callback(
    Output("right_overview_indicator", "children"),
    [
        Input("market_unit_dropdown", "value"),
        Input("product_dropdown", "value"),
        Input("opportunities_df", "data"),
    ],
)
def indicator3_callback(market_unit, product, df):
    df = pd.read_json(df, orient="split")
    won = millify(str(df[df["IsWon"] == 1]["Amount"].count()))
    return dcc.Markdown("**{}**".format(won))
