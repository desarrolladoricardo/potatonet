import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

# =============================
# Scraping helpers (DEMO)
# =============================

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_tierragro_fertilizante():
    """
    Demo: estructura para leer un fertilizante papa en Tierragro.
    Verifica robots.txt del sitio y ajusta la URL antes de usar en producción.
    """
    url = "https://www.tierragro.com/products/13-26-6-bulto-x-50-kgs"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    name = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Fertilizante 13-26-6 Tierragro"

    price_tag = soup.select_one("span[class*='price-item']")
    if price_tag:
        price_text = price_tag.get_text(strip=True)
    else:
        price_text = "0"

    return {
        "sitio": "Tierragro",
        "tipo": "Fertilizante",
        "producto": name,
        "presentacion": "Bulto 50 kg",
        "precio_raw": price_text,
        "url": url,
    }


def get_croper_fertilizante():
    """
    Demo: estructura para leer un fertilizante papa en Croper.
    Ajusta la URL a un producto específico permitido.
    """
    url = "https://croper.com/products/5-10-20-20-papa"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    name = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Fertilizante Forkamix 10-20-20"

    price_tag = soup.select_one("span[class*='price']")
    price_text = price_tag.get_text(strip=True) if price_tag else "0"

    return {
        "sitio": "Croper",
        "tipo": "Fertilizante",
        "producto": name,
        "presentacion": "Bulto 50 kg",
        "precio_raw": price_text,
        "url": url,
    }


# =============================
# Normalización de precios
# =============================

import re


def parse_price_to_float(text):
    if not text:
        return None
    text = text.replace(".", "").replace(" ", "").replace("COP", "").replace("$", "")
    m = re.search(r"(\d+)", text)
    return float(m.group(1)) if m else None


# =============================
# Dataset (intenta scraping, si falla usa dummy)
# =============================

rows = []
for fn in (get_tierragro_fertilizante, get_croper_fertilizante):
    try:
        item = fn()
        item["precio"] = parse_price_to_float(item["precio_raw"])
        rows.append(item)
    except Exception:
        pass

if not rows:
    # Datos de respaldo por si el scraping falla
    rows = [
        {
            "sitio": "Tierragro",
            "tipo": "Fertilizante",
            "producto": "Fertilizante 13-26-6",
            "presentacion": "Bulto 50 kg",
            "precio_raw": "$180.000",
            "precio": 180000,
            "url": "https://www.tierragro.com/products/13-26-6-bulto-x-50-kgs",
        },
        {
            "sitio": "Croper",
            "tipo": "Fertilizante",
            "producto": "Forkamix 10-20-20",
            "presentacion": "Bulto 50 kg",
            "precio_raw": "$150.000",
            "precio": 150000,
            "url": "https://croper.com/products/5-10-20-20-papa",
        },
    ]

df = pd.DataFrame(rows)

# Ordenar por precio ascendente para ver el más económico primero
if "precio" in df.columns:
    df = df.sort_values("precio", ascending=True)

# Guardar CSV (opcional)
df.to_csv("comparador_insumos_papa.csv", index=False)

# =============================
# Dashboard con Dash + Plotly
# =============================

app = Dash(__name__)

colors = {
    "background": "#0f172a",
    "card": "#1e293b",
    "primary": "#22c55e",
    "accent": "#38bdf8",
    "text": "#f9fafb",
}

app.layout = html.Div(
    style={"backgroundColor": colors["background"], "minHeight": "100vh", "padding": "20px"},
    children=[
        html.H1(
            "Comparador de precios insumos papa",
            style={"textAlign": "center", "color": colors["primary"], "marginBottom": "5px"},
        ),
        html.P(
            "Dashboard interactivo: selecciona el tipo de insumo y compara precios por sitio.",
            style={"textAlign": "center", "color": colors["text"], "marginBottom": "20px"},
        ),
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={
                        "flex": "1 1 280px",
                        "backgroundColor": colors["card"],
                        "padding": "15px",
                        "borderRadius": "12px",
                        "boxShadow": "0 10px 30px rgba(0,0,0,0.5)",
                    },
                    children=[
                        html.Label(
                            "Tipo de insumo",
                            style={"color": colors["text"], "fontWeight": "bold"},
                        ),
                        dcc.Dropdown(
                            id="tipo-dropdown",
                            options=[
                                {"label": t, "value": t} for t in sorted(df["tipo"].dropna().unique())
                            ],
                            value=df["tipo"].dropna().unique()[0] if not df.empty else None,
                            style={"backgroundColor": "#020617", "color": "#0f172a"},
                            clearable=False,
                        ),
                        html.Br(),
                        html.Div(
                            id="card-mejor-precio",
                            style={"color": colors["text"], "fontSize": "14px"},
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "flex": "2 1 400px",
                        "backgroundColor": colors["card"],
                        "padding": "15px",
                        "borderRadius": "12px",
                        "boxShadow": "0 10px 30px rgba(0,0,0,0.5)",
                    },
                    children=[
                        dcc.Graph(id="grafico-precios"),
                    ],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            style={
                "backgroundColor": colors["card"],
                "padding": "15px",
                "borderRadius": "12px",
                "boxShadow": "0 10px 30px rgba(0,0,0,0.5)",
            },
            children=[
                html.H3("Tabla detallada", style={"color": colors["accent"]}),
                dash_table.DataTable(
                    id="tabla-insumos",
                    columns=[{"name": c, "id": c} for c in df.columns],
                    data=df.to_dict("records"),
                    style_header={"backgroundColor": "#020617", "color": colors["text"], "fontWeight": "bold"},
                    style_cell={
                        "backgroundColor": colors["card"],
                        "color": colors["text"],
                        "border": "1px solid #020617",
                        "fontSize": 12,
                    },
                    page_size=10,
                ),
            ],
        ),
    ],
)


@app.callback(
    [Output("grafico-precios", "figure"), Output("card-mejor-precio", "children")],
    [Input("tipo-dropdown", "value")],
)
def actualizar_vistas(tipo):
    if not tipo:
        return px.scatter(), ""

    dff = df[df["tipo"] == tipo]

    fig = px.bar(
        dff,
        x="sitio",
        y="precio",
        color="sitio",
        hover_data=["producto", "presentacion", "precio_raw", "url"],
        color_discrete_sequence=["#22c55e", "#38bdf8", "#eab308", "#f97316", "#ec4899"],
    )
    fig.update_layout(
        plot_bgcolor="#020617",
        paper_bgcolor="#1e293b",
        font_color="#e5e7eb",
        title=f"Precios por sitio - {tipo}",
    )

    if not dff.empty and dff["precio"].notna().any():
        best = dff.sort_values("precio").iloc[0]
        texto = [
            html.P(
                f"Más económico: {best['producto']} ({best['presentacion']})",
                style={"margin": "0 0 4px 0"},
            ),
            html.P(
                f"Sitio: {best['sitio']} - Precio: {best['precio_raw']}",
                style={"margin": "0 0 4px 0", "color": "#22c55e", "fontWeight": "bold"},
            ),
            html.A("Ver producto", href=best["url"], target="_blank", style={"color": "#38bdf8"}),
        ]
    else:
        texto = "Sin datos de precio para este tipo de insumo."

    return fig, texto


if __name__ == "__main__":
    app.run(debug=True)
