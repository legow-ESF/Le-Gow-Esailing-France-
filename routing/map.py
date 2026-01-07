import json
import folium

# on lit le track
with open("track.json") as f:
    track = json.load(f)

# centre la carte sur le départ
start = track[0]

m = folium.Map(location=start, zoom_start=6, tiles="OpenStreetMap")

# trace la route
folium.PolyLine(
    locations=[(lat, lon) for lat, lon in track],
    weight=4,
    color="blue"
).add_to(m)

# marqueurs départ / arrivée
folium.Marker(track[0], tooltip="Départ", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(track[-1], tooltip="Arrivée", icon=folium.Icon(color="red")).add_to(m)

m.save("route.html")
print("Carte créée -> route.html")
