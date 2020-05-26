import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def Header_mgmt(app, dashboard_active, drilldown_active, report_active, Homepage_active):
    return html.Div([get_header_mgmt(app, dashboard_active, drilldown_active, report_active, Homepage_active)])

def Header_contract(app, simulation_active, library_active, contract_active, Homepage_active):
    return html.Div([get_header_contract(app, simulation_active, library_active, contract_active, Homepage_active)])


def get_header_mgmt(app, dashboard_active, drilldown_active, report_active, Homepage_active):
    menu = dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                        "Dashboard",
                        href="/vbc-demo/contract-manager/",
                        className="nav-link",
                        active = dashboard_active,
                        ),
                className="tab  first",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Drilldown",
                        href="/vbc-demo/contract-manager-drilldown/",
                        className="nav-link",
                        active = drilldown_active,
                        ),
                className="tab",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Report Generator",
                        href="/vbc-demo/contract-manager/report-generator/",
                        className="nav-link",
                        active = report_active,
                        ),
                className="tab",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Back to Homepage", 
                        href="/vbc-demo/launch/", 
                        className="nav-link",
                        active = Homepage_active,
                        ),
                className="tab",
                ),
        ],
        pills = True, 
        navbar = True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",)

    header = dbc.Navbar(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=app.get_asset_url("logo-demo.png"), style={"height":"4rem", "padding-top":"1px", "padding-left":"2rem"})),
                            dbc.Col(dbc.NavbarBrand("Contract Manager", className="ml-2", style={"font-family":"NotoSans-Black","font-size":"1.5rem","color":"#bfd4ff"})),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(menu, id="navbar-collapse", navbar=True),
                ],
            color="#fff",
            sticky = "top",
            expand = True,
            className="sticky-top",
            style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)"}
#            dark=True,
        )
    return header

def get_header_contract(app, simulation_active, library_active, contract_active, Homepage_active):

    menu = dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                        "Contract Simulation",
                        href="/vbc-demo/contract-optimizer/",
                        className="nav-link",
                        active = simulation_active,
                        ),
                className="tab first",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Measures Library",
                        href="/vbc-demo/contract-optimizer/measures-library/",
                        className="nav-link",
                        active = library_active,
                        ),
                className="tab",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Contract Generator",
                        #href="/vbc-demo/contract-optimizer/contract-generator/",
                        className="nav-link",
                        active = contract_active,
                        ),
                className="tab",
                ),
            dbc.NavItem(dbc.NavLink(
                        "Back to Homepage", 
                        href="/vbc-demo/launch/", 
                        className="nav-link",
                        active = Homepage_active
                        ),
                className="tab",
                ),
        ],
        pills = True, 
        navbar = True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",)

    header = dbc.Navbar(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=app.get_asset_url("logo-demo.png"), style={"height":"4rem", "padding-top":"1px"})),
                            dbc.Col(dbc.NavbarBrand("Contract Optimizer", className="ml-2", style={"font-family":"NotoSans-Black","font-size":"1.5rem","color":"#bfd4ff"})),
                            ],

                        align="center",
                        no_gutters=True,
                    ),

                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(menu, id="navbar-collapse", navbar=True),
                ],
            color="#fff",
            sticky = "top",
            expand = True,
            style={"box-shadow":"0 4px 8px 0 rgba(0, 0, 0, 0.05), 0 6px 20px 0 rgba(0, 0, 0, 0.05)"}
#            dark=True,
        )      
    return header



def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
