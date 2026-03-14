import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column

# Load dataset
df = pd.read_csv("C:\\Users\\MSI\\Downloads\\bokeh_project\\earthquakes_app\\earthquakes.csv")

# Remove rows with missing coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Convert latitude & longitude to Web Mercator
def mercator_projection(lat, lon):
    k = 6378137
    x = lon * (k * np.pi / 180)
    y = np.log(np.tan((90 + lat) * np.pi / 360)) * k
    return x, y

df["x"], df["y"] = mercator_projection(df["latitude"], df["longitude"])

# Data source
source = ColumnDataSource(df)

# World map tiles
tile_provider = get_provider(Vendors.CARTODBPOSITRON)

# Map figure
p = figure(
    x_axis_type="mercator",
    y_axis_type="mercator",
    title="Earthquake Dashboard",
    width=900,
    height=600,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)

# Add world map
p.add_tile(tile_provider)

# Plot earthquake points
p.circle(
    x="x",
    y="y",
    size=8,
    fill_color="red",
    fill_alpha=0.7,
    line_color=None,
    source=source
)

# Hover information
hover = HoverTool(tooltips=[
    ("Place", "@place"),
    ("Magnitude", "@mag"),
    ("Time", "@time")
])

p.add_tools(hover)

# Layout
layout = column(p)

curdoc().add_root(layout)
curdoc().title = "Earthquake Dashboard"
