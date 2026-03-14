import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Slider
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column


df = pd.read_csv("C:\\Users\\MSI\\Downloads\\bokeh_project\\earthquakes_app\\earthquakes.csv")
df = df.dropna(subset=["latitude", "longitude", "mag"])


def mercator_projection(lat, lon):
    k = 6378137
    x = lon * (k * np.pi / 180)
    y = np.log(np.tan((90 + lat) * np.pi / 360)) * k
    return x, y

df["x"], df["y"] = mercator_projection(df["latitude"], df["longitude"])


source = ColumnDataSource(df)


tile_provider = get_provider(Vendors.CARTODBPOSITRON)

p = figure(
    title="Global Earthquake Dashboard",
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=900,
    height=600,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)

p.add_tile(tile_provider)


p.circle(
    x="x",
    y="y",
    size="mag",
    fill_color="red",
    fill_alpha=0.6,
    line_color=None,
    source=source
)


hover = HoverTool(tooltips=[
    ("Place", "@place"),
    ("Magnitude", "@mag"),
    ("Time", "@time")
])
p.add_tools(hover)


slider = Slider(start=0, end=8, value=0, step=0.1, title="Minimum Magnitude")

def update(attr, old, new):
    filtered = df[df["mag"] >= slider.value]
    source.data = ColumnDataSource(filtered).data

slider.on_change("value", update)


layout = column(slider, p)
curdoc().add_root(layout)
curdoc().title = "Earthquake Dashboard"