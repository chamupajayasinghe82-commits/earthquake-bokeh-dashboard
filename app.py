import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, ColorBar, LinearColorMapper
from bokeh.layouts import column
from bokeh.tile_providers import get_provider, Vendors
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.transform import linear_cmap

# Load dataset
df = pd.read_csv("earthquakes.csv")
df = df.dropna(subset=["latitude", "longitude", "mag"])

df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)
df["mag"] = df["mag"].astype(float)

df = df[df["mag"] > 0]

# Convert lat/lon to Web Mercator
def latlon_to_mercator(lat, lon):
    k = 6378137
    x = lon * (k * np.pi / 180)
    y = np.log(np.tan((90 + lat) * np.pi / 360)) * k
    return x, y

df["x"], df["y"] = latlon_to_mercator(df["latitude"], df["longitude"])

# Circle size based on magnitude
df["size"] = df["mag"] * 3 + 2

source = ColumnDataSource(df)

# Color mapper
mapper = LinearColorMapper(palette="Inferno256",
                           low=df["mag"].min(),
                           high=df["mag"].max())

# Map tile
tile_provider = get_provider(Vendors.CARTODBPOSITRON)

# Create map
p = figure(
    title="🌍 Global Earthquake Dashboard",
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=900,
    height=600,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)

p.add_tile(tile_provider)

# Earthquake points
p.circle(
    x="x",
    y="y",
    size="size",
    fill_color=linear_cmap('mag', 'Inferno256',
                           df["mag"].min(),
                           df["mag"].max()),
    fill_alpha=0.7,
    line_color=None,
    source=source
)

# Hover info
hover = HoverTool(tooltips=[
    ("Place", "@place"),
    ("Magnitude", "@mag"),
    ("Time", "@time"),
    ("Latitude", "@latitude"),
    ("Longitude", "@longitude")
])

p.add_tools(hover)

# Color bar
color_bar = ColorBar(color_mapper=mapper, title="Magnitude")
p.add_layout(color_bar, 'right')

layout = column(p)

# Export HTML
html = file_html(layout, CDN, "Earthquake Dashboard")

with open("index.html", "w") as f:
    f.write(html)

print("index.html generated!")
