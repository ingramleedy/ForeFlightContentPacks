import re

base_kml_file = "base_timezones.kml"
enhanced_kml_file = "TimeZones_Perfect.kml"

print("Creating ultra-transparent fill with solid borders and clean UTC-05:00 labels...")

with open(base_kml_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# === MAPPING (kept only for rich balloon details) ===
offset_mappings = {
    "-12:00": {"name": "International Date Line West", "cities": "Baker Island", "dst": "No", "mil": "Yankee"},
    "-11:00": {"name": "Samoa Standard Time", "cities": "Pago Pago", "dst": "No", "mil": "X-ray"},
    "-10:00": {"name": "Hawaii-Aleutian Time", "cities": "Honolulu", "dst": "No", "mil": "Whiskey"},
    "-09:00": {"name": "Alaska Standard Time", "cities": "Anchorage", "dst": "Yes", "mil": "Victor"},
    "-08:00": {"name": "Pacific Standard Time", "cities": "Los Angeles", "dst": "Yes", "mil": "Uniform"},
    "-07:00": {"name": "Mountain Standard Time", "cities": "Denver", "dst": "Yes", "mil": "Tango"},
    "-06:00": {"name": "Central Standard Time", "cities": "Chicago", "dst": "Yes", "mil": "Sierra"},
    "-05:00": {"name": "Eastern Standard Time", "cities": "New York", "dst": "Yes", "mil": "Romeo"},
    "-04:00": {"name": "Atlantic Standard Time", "cities": "Halifax", "dst": "Varies", "mil": "Quebec"},
    "-03:00": {"name": "Brazil/Argentina Time", "cities": "São Paulo", "dst": "No", "mil": "Papa"},
    "+00:00": {"name": "UTC / Greenwich Mean Time", "cities": "London", "dst": "Varies", "mil": "Zulu"},
    "+01:00": {"name": "Central European Time", "cities": "Paris", "dst": "Yes", "mil": "Alpha"},
    "+02:00": {"name": "Eastern European Time", "cities": "Athens", "dst": "Varies", "mil": "Bravo"},
    "+03:00": {"name": "Moscow / East Africa Time", "cities": "Moscow", "dst": "No", "mil": "Charlie"},
    "+08:00": {"name": "China Standard Time", "cities": "Beijing", "dst": "No", "mil": "Hotel"},
    "+09:00": {"name": "Japan / Korea Time", "cities": "Tokyo", "dst": "No", "mil": "India"},
    "+10:00": {"name": "Australian Eastern Time", "cities": "Sydney", "dst": "Yes", "mil": "Kilo"},
}

# Very transparent fill (alpha = 40 ≈ 25% opacity)
# Solid border: use full opaque version of the same color (alpha = ff)
color_map_fill = {
    "-12:00": "4000ffff",
    "-11:00": "4000ff99",
    "-10:00": "4000ccff",
    "-09:00": "400099ff",
    "-08:00": "400066ff",
    "-07:00": "400033ff",
    "-06:00": "400000ff",
    "-05:00": "40ff00ff",
    "-04:00": "40ff0099",
    "-03:00": "40ff0066",
    "+00:00": "40ff0000",
    "+01:00": "40ff9900",
    "+02:00": "40ffcc00",
    "+03:00": "40ffff00",
    "+08:00": "4000ff00",
    "+09:00": "4033ff00",
    "+10:00": "4066ff00",
}
default_fill = "40aaaaaa"

# Solid line colors (full opacity: alpha = ff)
color_map_line = {
    "-12:00": "ff00ffff",
    "-11:00": "ff00ff99",
    "-10:00": "ff00ccff",
    "-09:00": "ff0099ff",
    "-08:00": "ff0066ff",
    "-07:00": "ff0033ff",
    "-06:00": "ff0000ff",
    "-05:00": "ffff00ff",
    "-04:00": "ffff0099",
    "-03:00": "ffff0066",
    "+00:00": "ffff0000",
    "+01:00": "ffff9900",
    "+02:00": "ffffcc00",
    "+03:00": "ffffff00",
    "+08:00": "ff00ff00",
    "+09:00": "ff33ff00",
    "+10:00": "ff66ff00",
}
default_line = "ffaaaaaa"

# Longitude centers
lon_centers = {
    "-12:00": "-180",
    "-11:00": "-165",
    "-10:00": "-150",
    "-09:00": "-135",
    "-08:00": "-120",
    "-07:00": "-105",
    "-06:00": "-90",
    "-05:00": "-75",
    "-04:00": "-60",
    "-03:00": "-45",
    "+00:00": "0",
    "+01:00": "15",
    "+02:00": "30",
    "+03:00": "45",
    "+08:00": "120",
    "+09:00": "135",
    "+10:00": "150",
}

fixed_latitude = "45"

output = []
in_document = False
placemark_lines = []
inside_placemark = False
count = 0

for line in lines:
    stripped = line.strip()

    if not in_document:
        output.append(line)
        if stripped == "<Document>":
            in_document = True
        continue

    if stripped.startswith("<Placemark"):
        inside_placemark = True
        placemark_lines = [line]
        continue

    if inside_placemark:
        placemark_lines.append(line)
        if stripped == "</Placemark>":
            inside_placemark = False
            ptext = "".join(placemark_lines)

            # Extract original name
            name_match = re.search(r"<name>(.*?)</name>", ptext)
            original_raw = name_match.group(1).strip() if name_match else "UTC+00:00"

            # Robust offset extraction
            if original_raw.startswith(("GMT", "UTC")):
                prefix_len = 3 if original_raw[3] in "+-" else 4
                offset_part = original_raw[prefix_len:].strip()
                if len(offset_part) == 4 and offset_part[0] in "+-":
                    offset = offset_part[:3] + ":00"
                elif len(offset_part) == 5 and ":" not in offset_part:
                    offset = offset_part[:3] + ":" + offset_part[3:]
                else:
                    offset = offset_part if offset_part.startswith(("+", "-")) else "+" + offset_part
            else:
                offset = "+00:00"

            info = offset_mappings.get(offset, {"name": original_raw, "cities": "Various", "dst": "Varies", "mil": "—"})

            # Clean label: "UTC-05:00"
            clean_label = f"UTC{offset}"

            desc = f"""<![CDATA[
<h3>{offset} Time Zone</h3>
<p><b>Offset:</b> UTC{offset}</p>
<p><b>Name:</b> {info['name']}</p>
<p><b>DST:</b> {info['dst']}</p>
<p><b>Military:</b> {info['mil']}</p>
<p><b>Cities:</b> {info['cities']}</p>
]]>"""

            # Update placemark name
            ptext = re.sub(r"<name>.*?</name>", f"<name>{clean_label}</name>", ptext)

            # Update description
            if "<description>" in ptext:
                ptext = re.sub(r"<description>.*?</description>", "<description>" + desc + "</description>", ptext, flags=re.DOTALL)
            else:
                ptext = ptext.replace("</name>", "</name>\n  <description>" + desc + "</description>", 1)

            # Remove styleUrl
            ptext = re.sub(r"\s*<styleUrl>.*?</styleUrl>\s*", "", ptext)

            # Colors: very transparent fill, solid line
            fill_color = color_map_fill.get(offset, default_fill)
            line_color = color_map_line.get(offset, default_line)
            lon = lon_centers.get(offset, "0")

            point_block = f"""    <Point>
      <coordinates>{lon},{fixed_latitude},0</coordinates>
    </Point>
"""

            style_block = f"""  <Style>
    <IconStyle>
      <scale>0.0</scale>
    </IconStyle>
    <LabelStyle>
      <color>ffffffff</color>
      <scale>1.8</scale>
    </LabelStyle>
    <LineStyle>
      <color>{line_color}</color>  <!-- Solid full-opacity border -->
      <width>1</width>
    </LineStyle>
    <PolyStyle>
      <color>{fill_color}</color>  <!-- Very transparent fill -->
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
"""

            # Insert style
            if "<description>" in ptext:
                ptext = ptext.replace("</description>", "</description>\n" + style_block, 1)
            else:
                ptext = ptext.replace("</name>", "</name>\n" + style_block, 1)

            # Add Point
            if "<MultiGeometry>" in ptext:
                ptext = ptext.replace("</MultiGeometry>", point_block + "\n  </MultiGeometry>", 1)
            elif "<Polygon>" in ptext:
                ptext = re.sub(r"<Polygon>", "<MultiGeometry>\n    <Polygon>", ptext)
                ptext = re.sub(r"</Polygon>", "</Polygon>\n" + point_block + "\n  </MultiGeometry>", ptext)

            for pl in ptext.splitlines(keepends=True):
                output.append(pl)
            count += 1
            placemark_lines = []
        continue

    pass

output.append("</Document>\n")
output.append("</kml>\n")

with open(enhanced_kml_file, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(output)

print(f"\nSUCCESS! {count} time zones created.")
print(f"Saved: {enhanced_kml_file}")
print("")
print("Latest update:")
print("• Borders (LineStyle) now fully solid and opaque — crisp and visible")
print("• Fill remains ultra-transparent (~25% opacity) — subtle overlay")
print("• Clean 'UTC-05:00' labels on map and in Places panel")
print("• Full details in info balloon on click")
print("")
print("Perfect balance: clear boundaries with minimal visual interference!")