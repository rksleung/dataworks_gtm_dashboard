import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import sf_manager, app
from panels import overview, opportunities, cases, leads


server = app.server

app.layout = html.Div(
    [
        html.Div(
            className="row header",
            children=[
                html.Button(id="menu", children=dcc.Markdown("&#8801")),
                html.Img(src=app.get_asset_url("oshin-logo-new-white-2.png")),
                html.A(
                    id="learn_more",
                    children=html.Button("Learn More"),
                    href="https://www.dataworksbi.com",
                ),
            ],
        ),
        html.Div(
            id="tabs",
            className="row tabs",
            children=[
                dcc.Link("Overview", href="/"),
                dcc.Link("Opportunities", href="/"),
                dcc.Link("Leads", href="/"),
                dcc.Link("Cases", href="/"),
            ],
        ),
        html.Div(
            id="mobile_tabs",
            className="row tabs",
            style={"display": "none"},
            children=[
                dcc.Link("Overview", href="/"),
                dcc.Link("Opportunities", href="/"),
                dcc.Link("Leads", href="/"),
                dcc.Link("Cases", href="/"),
            ],
        ),
        dcc.Store(  # finance df
            id="finance_df",
            data="data/df_actual_vs_budget.csv",
            #data=csv_manager.get_data(),
        ),
        dcc.Store(  # opportunities df
            id="opportunities_df",
            data=sf_manager.get_opportunities().to_json(orient="split"),
        ),
        dcc.Store(  # leads df
            id="leads_df", data=sf_manager.get_leads().to_json(orient="split")
        ),
        dcc.Store(
            id="cases_df", data=sf_manager.get_cases().to_json(orient="split")
        ),  # cases df
        dcc.Location(id="url", refresh=False),
        html.Div(id="tab_content"),
        html.Link(
            href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
            rel="stylesheet",
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"
        ),
        html.Link(
            href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"
        ),
    ],
    className="row",
    style={"margin": "0%"},
)

# Update the index


@app.callback(
    [
        Output("tab_content", "children"),
        Output("tabs", "children"),
        Output("mobile_tabs", "children"),
    ],
    [Input("url", "pathname")],
)
def display_page(pathname):
    tabNames = [
        {'name':"Overview", 'path':"/panel/overview"},
        {'name':"Opportunities", 'path':"/panel/opportunities"},
        {'name':"Leads", 'path':"/panel/leads"},
        {'name':"Cases", 'path':"/panel/cases"},
    ]
    tabs = []
    for tabName in tabNames:
        tabs.append(dcc.Link(tabName['name'], href=tabName['path']))
    for idx, tabName in enumerate(tabNames):
        if tabName['path'] == pathname:
            tabs[idx] = dcc.Link(
                dcc.Markdown("**&#9632 " + tabName['name'] + "**"),
                href=pathname,
            )
            return globals()[tabName['name'].lower()].layout, tabs, tabs
    return globals()[tabNames[0]['name'].lower()].layout, tabs, tabs


@app.callback(
    Output("mobile_tabs", "style"),
    [Input("menu", "n_clicks")],
    [State("mobile_tabs", "style")],
)
def show_menu(n_clicks, tabs_style):
    if n_clicks:
        if tabs_style["display"] == "none":
            tabs_style["display"] = "flex"
        else:
            tabs_style["display"] = "none"
    return tabs_style


if __name__ == "__main__":
    app.run_server(debug=True)
