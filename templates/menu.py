
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
import dash


PLOTLY_LOGO = "assets\ComaisLab.png"

nav_item = dbc.NavItem(dbc.NavLink("AutoCorrelação", href="http://municipios.comais.uft.edu.br/autocorrelations"))
nav_item_comais = dbc.NavItem(dbc.NavLink("Comais Lab", href="http://www.comais.uft.edu.br/"))
nav_item_home = dbc.NavItem(dbc.NavLink("Home", href="http://municipios.comais.uft.edu.br/"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Entry 1"),
        dbc.DropdownMenuItem("Entry 2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Entry 3"),
    ],
    nav=True,
    in_navbar=True,
    label="Menu",
)



custom_default = dbc.Navbar(
    dbc.Container(
        [
            dbc.Col( html.Img(src=PLOTLY_LOGO, height="40px")),
            dbc.NavbarBrand("Índice de Governança Municipal ", href="http://municipios.comais.uft.edu.br"),
            dbc.NavbarToggler(id="navbar-toggler1"),
 
            dbc.Collapse(
                dbc.Nav(
                    [nav_item_home, nav_item,nav_item_comais ], className="ms-auto", navbar=True
                ),
            
                id="navbar-collapse1",
                navbar=True,
            ),
        ]
    ),
    className="mb-1",
)


# custom navbar based on https://getbootstrap.com/docs/4.1/examples/dashboard/
dashboard = dbc.Navbar(
    dbc.Container(
        [
            dbc.Col(dbc.NavbarBrand("Dashboard", href="#"), sm=3, md=2),
            dbc.Col(dbc.Input(type="search", placeholder="Search here")),
            dbc.Col(
                dbc.Nav(
                    dbc.Container(dbc.NavItem(dbc.NavLink("Sign out"))),
                    navbar=True,
                ),
                width="auto",
            ),
        ],
    ),
    color="dark",
    dark=True,
)



def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
