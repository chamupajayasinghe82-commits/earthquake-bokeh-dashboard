import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CustomJS, Slider
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column
from bokeh.embed import file_html
from bokeh.resources import CDN

# Load dataset
df = pd.read_csv("C:\\Users\\MSI\\Downloads\\bokeh_project\\earthquakes_app\\earthquakes.csv")
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)
df["mag"] = df["mag"].astype(float)
df = df.dropna(subset=["latitude", "longitude", "mag"])

def latlon_to_mercator(lat, lon):
    k = 6378137
    x = lon * (k * np.pi / 180)
    y = np.log(np.tan((90 + lat) * np.pi / 360)) * k
    return x, y

df["x"], df["y"] = latlon_to_mercator(df["latitude"], df["longitude"])
df["size"] = df["mag"] * 3 + 2

source = ColumnDataSource(df)
full_source = ColumnDataSource(df)

tile_provider = get_provider(Vendors.CARTODBPOSITRON)

p = figure(
    title="Global Earthquake Dashboard",
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=900, height=600,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)
p.add_tile(tile_provider)

circles = p.circle(
    x="x", y="y", size="size",
    fill_color="red", fill_alpha=0.6,
    line_color=None, source=source
)

hover = HoverTool(tooltips=[
    ("Place", "@place"),
    ("Magnitude", "@mag"),
    ("Time", "@time")
])
p.add_tools(hover)

slider = Slider(start=0, end=10, value=0, step=0.1, title="Minimum Magnitude")

# Use CustomJS instead of Python callback
callback = CustomJS(args=dict(source=source, full=full_source, slider=slider), code="""
    const min_mag = slider.value;
    const full_data = full.data;
    const new_data = {x: [], y: [], mag: [], place: [], time: [], size: []};
    for (let i = 0; i < full_data['mag'].length; i++) {
        if (full_data['mag'][i] >= min_mag) {
            new_data['x'].push(full_data['x'][i]);
            new_data['y'].push(full_data['y'][i]);
            new_data['mag'].push(full_data['mag'][i]);
            new_data['place'].push(full_data['place'][i]);
            new_data['time'].push(full_data['time'][i]);
            new_data['size'].push(full_data['size'][i]);
        }
    }
    source.data = new_data;
""")

slider.js_on_change('value', callback)

layout = column(slider, p)

html = file_html(layout, CDN, "Earthquake Dashboard")
with open("index.html", "w") as f:
    f.write(html)

print("index.html generated!")