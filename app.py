import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CustomJS, Slider, ColorBar, LinearColorMapper
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
df["size"] = df["mag"] * 3 + 2

source = ColumnDataSource(df)
full_source = ColumnDataSource(df)

# Color mapper based on magnitude
mapper = LinearColorMapper(palette="Inferno256", low=df['mag'].min(), high=df['mag'].max())

# Create map figure
tile_provider = get_provider(Vendors.CARTODBPOSITRON)

p = figure(
    title="🌍 Global Earthquake Dashboard",
    x_axis_type="mercator",
    y_axis_type="mercator",
    width=900, height=600,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)
p.add_tile(tile_provider)

# Circle glyphs with color and size
p.circle(
    x="x", y="y", size="size",
    fill_color=linear_cmap('mag', 'Inferno256', df['mag'].min(), df['mag'].max()),
    fill_alpha=0.7, line_color=None,
    source=source
)

# Hover tool
hover = HoverTool(tooltips=[
    ("Place", "@place"),
    ("Magnitude", "@mag"),
    ("Time", "@time"),
    ("Latitude", "@latitude"),
    ("Longitude", "@longitude")
])
p.add_tools(hover)

# Color bar for magnitude
color_bar = ColorBar(color_mapper=mapper, location=(0,0), title="Magnitude")
p.add_layout(color_bar, 'right')

# Slider for filtering by minimum magnitude
slider = Slider(start=0, end=10, value=0, step=0.1, title="Minimum Magnitude")

callback = CustomJS(args=dict(source=source, full=full_source, slider=slider), code="""
    const min_mag = slider.value;
    const full_data = full.data;
    const new_data = {x: [], y: [], mag: [], place: [], time: [], size: [], latitude: [], longitude: []};
    for (let i = 0; i < full_data['mag'].length; i++) {
        if (full_data['mag'][i] >= min_mag) {
            new_data['x'].push(full_data['x'][i]);
            new_data['y'].push(full_data['y'][i]);
            new_data['mag'].push(full_data['mag'][i]);
            new_data['place'].push(full_data['place'][i]);
            new_data['time'].push(full_data['time'][i]);
            new_data['size'].push(full_data['size'][i]);
            new_data['latitude'].push(full_data['latitude'][i]);
            new_data['longitude'].push(full_data['longitude'][i]);
        }
    }
    source.data = new_data;
""")

slider.js_on_change('value', callback)

layout = column(slider, p)

# Export to HTML
html = file_html(layout, CDN, "Earthquake Dashboard")
with open("index.html", "w") as f:
    f.write(html)

print("index.html generated!")
