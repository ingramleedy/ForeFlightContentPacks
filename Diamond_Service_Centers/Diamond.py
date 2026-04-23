import requests
from bs4 import BeautifulSoup
from html import escape

# URL of the Diamond Aircraft map data
URL = "https://www.diamondaircraft.com/en/map.xhr"


def safe_text(text):
    """Escape only & in text content (leave < and > for real HTML tags)"""
    if not text:
        return ""
    return text.replace('&', '&amp;')


def parse_info_window(html):
    """Parse infoWindow and return RAW HTML string with real tags for CDATA"""
    if not html:
        return "No details available"

    soup = BeautifulSoup(html, 'html.parser')
    description_parts = []

    # Category
    category_div = soup.find('div', class_='category')
    if category_div:
        cat_text = safe_text(category_div.get_text(strip=True))
        description_parts.append(f"<strong>Category:</strong> {cat_text}")

    # Company name
    company_div = soup.find('div', class_='company')
    if company_div and company_div.find('p'):
        company_text = safe_text(company_div.find('p').get_text(strip=True))
        description_parts.append(f"<strong>Company:</strong> {company_text}")

    # Address
    address_div = soup.find('div', class_='address')
    if address_div and address_div.find('p'):
        addr_text = address_div.find('p').get_text(separator='\n', strip=True)
        addr_lines = [safe_text(line) for line in addr_text.split('\n') if line.strip()]
        description_parts.append("<strong>Address:</strong>")
        description_parts.extend(addr_lines)

    # Contact details
    details_div = soup.find('div', class_='details')
    if details_div:
        for a in details_div.find_all('a', href=True):
            a['target'] = '_blank'
            a['rel'] = 'noopener noreferrer'
        contact_html = str(details_div).replace('<br />', '<br/>')
        description_parts.append("<strong>Contact:</strong>")
        description_parts.append(contact_html)

    # Notes
    desc_div = soup.find('div', class_='description')
    if desc_div:
        notes_text = safe_text(desc_div.get_text(strip=True))
        if notes_text:
            description_parts.append(f"<strong>Notes:</strong> {notes_text}")

    return "<br/>".join(description_parts) if description_parts else "No details available"


def write_kml_file(filename, name, description, placemarks, style_id, icon_url):
    """Helper to write a single KML file"""
    styles = f'''
    <Style id="{style_id}">
        <IconStyle>
            <color>ff00aaff</color><scale>1.1</scale>
            <Icon><href>{icon_url}</href></Icon>
        </IconStyle>
    </Style>'''

    if style_id == "distributorStyle":
        styles = styles.replace('ff00aaff', 'ff00ff00').replace('airports.png', 'target.png')
    elif style_id == "flightSchoolStyle":
        styles = styles.replace('ff00aaff', 'ffff0000').replace('scale>1.1', 'scale>1.2').replace('airports.png',
                                                                                                  'schools.png')

    header = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{name}</name>
    <description>{description}</description>
{styles}
'''

    footer = '''
</Document>
</kml>
'''

    placemarks_str = '\n'.join(placemarks) if placemarks else ''

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(placemarks_str)
        f.write(footer)

    print(f"Saved: {filename} ({len(placemarks)} locations)")


def generate_separate_kmls():
    print(f"Fetching data from {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    json_data = response.json()

    addresses = json_data.get('addresses', [])
    print(f"Found {len(addresses)} total locations. Generating separate KML files...\n")

    # Group placemarks by category
    groups = {
        101: {'file': 'Diamond_Distributors.kml',
              'name': 'Diamond Aircraft - Sales / Distributors',
              'desc': 'Official Diamond Aircraft Sales Partners and Distributors worldwide.',
              'style': 'distributorStyle',
              'icon': 'http://maps.google.com/mapfiles/kml/shapes/target.png',
              'placemarks': []},
        102: {'file': 'Diamond_Service_Centers.kml',
              'name': 'Diamond Aircraft - Authorized Service Centers',
              'desc': 'Official Diamond Aircraft Authorized Service Centers worldwide.',
              'style': 'serviceCenterStyle',
              'icon': 'http://maps.google.com/mapfiles/kml/shapes/airports.png',
              'placemarks': []},
        103: {'file': 'Diamond_Training_Centers.kml',
              'name': 'Diamond Aircraft - Training / Flight Schools',
              'desc': 'Official Diamond Aircraft Training Centers and Flight Schools worldwide.',
              'style': 'flightSchoolStyle',
              'icon': 'http://maps.google.com/mapfiles/kml/shapes/schools.png',
              'placemarks': []},
    }

    other_placemarks = []

    for addr in addresses:
        name_raw = addr.get('name', 'Unnamed Location') or 'Unnamed Location'
        name = escape(name_raw.strip())
        lat = addr.get('lat')
        lng = addr.get('lng')
        category = addr.get('category', 102)
        info_window = addr.get('infoWindow', '')

        if lat is None or lng is None:
            print(f"Skipping '{name_raw}': missing coordinates")
            continue

        rich_desc_html = parse_info_window(info_window)

        style = 'serviceCenterStyle'
        if category == 101:
            style = 'distributorStyle'
        elif category == 103:
            style = 'flightSchoolStyle'

        placemark = f'''    <Placemark>
        <name>{name}</name>
        <description><![CDATA[{rich_desc_html}]]></description>
        <styleUrl>#{style}</styleUrl>
        <Point>
            <coordinates>{lng},{lat},0</coordinates>
        </Point>
    </Placemark>'''

        if category in groups:
            groups[category]['placemarks'].append(placemark)
        else:
            other_placemarks.append(placemark)

    # Write main category files
    for cat_data in groups.values():
        write_kml_file(
            filename=cat_data['file'],
            name=cat_data['name'],
            description=cat_data['desc'],
            placemarks=cat_data['placemarks'],
            style_id=cat_data['style'],
            icon_url=cat_data['icon']
        )

    # Write "Other" file if needed
    if other_placemarks:
        write_kml_file(
            filename='Diamond_Other_Locations.kml',
            name='Diamond Aircraft - Other / Unknown Categories',
            description='Diamond Aircraft locations with unknown or new category types.',
            placemarks=other_placemarks,
            style_id='serviceCenterStyle',
            icon_url='http://maps.google.com/mapfiles/kml/shapes/airports.png'
        )

    print("\nAll KML files generated successfully!")
    print("Open them individually in Google Earth or merge them as needed.")


if __name__ == "__main__":
    generate_separate_kmls()