# derived from 'mp2osm_ukraine.py' 
# modified by simon@mungewell.org
# modified by Karl Newman (User:SiliconFiend) to preserve routing topology and parse RouteParam 
# modified by Abdullah Abdulrhman (User:abdullahO2) https://github.com/abdullahO2
# license: GPL V2 or later
try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon, MultiPolygon, Point, LineString
    from shapely.ops import unary_union
    import xml.etree.ElementTree as ET
    import os
    from concurrent.futures import ThreadPoolExecutor
    from bidi.algorithm import get_display
    import arabic_reshaper
except ImportError:
    import pip
    import sys

    def install(package):
        pip.main(['install', package])

    install('geopandas')
    install('pandas')
    install('shapely')
    install('lxml')
    install('arabic_reshaper')
    install('python-bidi')




import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
from shapely.ops import unary_union
import xml.etree.ElementTree as ET
import os
from concurrent.futures import ThreadPoolExecutor
from bidi.algorithm import get_display
import arabic_reshaper

# تعريف الأنواع
## أنواع النقاط
POI_TAG_MAP = {
    # Cities المدن والقرى
    (0x0,): {'place': 'locality'},
    (0x0001,): {'place': 'city'},
    (0x0002,): {'place': 'city'},
    (0x0003,): {'place': 'city'},
    (0x0004,): {'place': 'city'},
    (0x0005,): {'place': 'city'},
    (0x0006,): {'place': 'city'},
    (0x0007,): {'place': 'city'},
    (0x0008,): {'place': 'city'},
    (0x0009,): {'place': 'town'},
    (0x000a,): {'place': 'town'},
    (0x000b,): {'place': 'village'},
    (0x000c,): {'place': 'hamlet'},
    (0x000d,): {'place': 'locality'},
    (0x000e,): {'place': 'locality'},
    (0x000f,): {'place': 'locality'},
    (0x0010,): {'place': 'locality'},
    (0x0100,): {'place': 'city'},
    (0x0200,): {'place': 'city'},
    (0x0300,): {'place': 'city'},
    (0x0400,): {'place': 'city'},
    (0x0500,): {'place': 'town'},
    (0x0600,): {'place': 'town'},
    (0x0700,): {'place': 'town'},
    (0x0800,): {'place': 'town'},
    (0x0900,): {'place': 'town'},
    (0x0a00,): {'place': 'town'},
    (0x0b00,): {'place': 'suburb'},
    (0x0c00,): {'place': 'hamlet'},
    (0x0d00,): {'place': 'hamlet'},
    (0x0e00,): {'place': 'village'},
    (0x0f00,): {'place': 'hamlet'},
    (0x1000,): {'place': 'hamlet'},
    (0x1100,): {'place': 'locality'},
    (0x1200,): {'place': 'locality'},
    (0x1400,): {'place': 'state'},
    (0x1500,): {'place': 'locality'},
    (0x1612,): {'highway': 'gate'},
    (0x1616,): {'highway': 'gate'},
    # Wrecks/Obstruction عوائق الطريق
    (0x1c00,): {'highway': 'other'},
    (0x1c01,): {'highway': 'wreck'},
    (0x1c02,): {'highway': 'wreck'},
    (0x1c03,): {'highway': 'wreck'},
    (0x1c04,): {'highway': 'wreck'},
    (0x1c05,): {'highway': 'obstruction'},
    (0x1c06,): {'highway': 'obstruction'},
    (0x1c07,): {'highway': 'obstruction'},
    (0x1c08,): {'highway': 'obstruction'},
    (0x1c09,): {'highway': 'obstruction'},
    (0x1c0a,): {'highway': 'obstruction'},
    (0x1c0b,): {'highway': 'obstruction'},
    # المناطق والأماكن الغير مأهولة
    (0x1e00,): {'place': 'region'},
    (0x1f00,): {'place': 'country'},
    (0x2800,): {'place': 'locality'},
    (0x2804,): {'place': 'locality'},
    (0x2900,): {'shop': 'mall'},
    # Food/Drink المطاعم
    (0x2a00,): {'amenity': 'restaurant'},
    (0x2a01,): {'amenity': 'restaurant'},
    (0x2a02,): {'amenity': 'restaurant'},
    (0x2a03,): {'amenity': 'fast_food'},
    (0x2a04,): {'amenity': 'fast_food'},
    (0x2a05,): {'shop': 'bakery'},
    (0x2a06,): {'amenity': 'fast_food'},
    (0x2a07,): {'amenity': 'fast_food'},
    (0x2a08,): {'amenity': 'fast_food'},
    (0x2a09,): {'amenity': 'fast_food'},
    (0x2a10,): {'amenity': 'fast_food'},
    (0x2a12,): {'amenity': 'ice_cream'},

    (0x2a0a,): {'amenity': 'fast_food'},
    (0x2a0b,): {'amenity': 'fast_food'},
    (0x2a0c,): {'amenity': 'fast_food'},
    (0x2a0d,): {'amenity': 'fast_food'},
    (0x2a0e,): {'amenity': 'cafe'},
    # Accomodation السكن
    (0x2b00,): {'tourism': 'hotel'},
    (0x2b01,): {'tourism': 'motel'},
    (0x2b02,): {'tourism': 'guest_house'},
    (0x2b03,): {'tourism': 'caravan_site'},
    (0x2b04,): {'tourism': 'guest_house'},
    # Attractions الأماكن الجذابة
    (0x2c00,): {'tourism': 'attraction'},
    (0x2c01,): {'tourism': 'theme_park'},
    (0x2c02,): {'historic': 'ruins'},
    (0x2c03,): {'amenity': 'library'},
    (0x2c04,): {'tourism': 'viewpoint'},
    (0x2c05,): {'amenity': 'school'},
    (0x2c06,): {'leisure': 'park'},
    (0x2c07,): {'amenity': 'zoo'},
    (0x2c08,): {'leisure': 'sports_centre'},
    (0x2c09,): {'amenity': 'public_building'},
    (0x2c0b,): {'amenity': 'place_of_worship'},
    (0x2c0c,): {'amenity': 'geiser'},
    (0x2c0d,): {'amenity': 'place_of_worship'},
    (0x2c0e,): {'amenity': 'place_of_worship'},
    (0x2c0f,): {'amenity': 'place_of_worship'},
    # الرياضة
    (0x2d05,): {'leisure': 'golf_course'},
    (0x2d02,): {'leisure': 'sports_centre'},
    (0x2d08,): {'leisure': 'sports_centre'},
    (0x2d09,): {'leisure': 'sports_centre'},
    (0x2d0a,): {'leisure': 'sports_centre'},
    (0x2d0b,): {'leisure': 'sports_centre'},
    # Shops المتاجر
    (0x2e00,): {'shop': 'convenience'},
    (0x2e01,): {'shop': 'convenience'},
    (0x2e02,): {'shop': 'supermarket'},
    (0x2e03,): {'shop': 'supermarket'},
    (0x2e04,): {'shop': 'supermarket'},
    (0x2e05,): {'amenity': 'pharmacy'},
    (0x2e06,): {'shop': 'convenience'},
    (0x2e07,): {'shop': 'convenience'},
    (0x2e08,): {'shop': 'convenience'},
    (0x2e09,): {'shop': 'convenience'},
    (0x2e0a,): {'shop': 'convenience'},
    (0x2e0b,): {'shop': 'convenience'},
    # Transport Services خدمات النقل
    (0x2f00,): {'shop': 'dry_cleaning'},
    (0x2f01,): {'amenity': 'fuel'},
    (0x2f02,): {'amenity': 'car_rental'},
    (0x2f03,): {'shop': 'car_repair'},
    (0x2f04,): {'aeroway': 'aerodrome'},
    (0x2f05,): {'amenity': 'post_office'},
    (0x2f06,): {'amenity': 'bank'},
    (0x2f07,): {'shop': 'car'},
    (0x2f08,): {'amenity': 'bus_station'},
    (0x2f09,): {'shop': 'marina_repair'},
    (0x2f0b,): {'amenity': 'parking'},
    (0x2f0c,): {'tourism': 'picnic_site'},
    (0x2f0d,): {'place': 'locality'},
    (0x2f0e,): {'amenity': 'car_wash'},
    (0x2f0f,): {'shop': 'mall'},
    (0x2f10,): {'services': 'other'},
    (0x2f11,): {'amenity': 'business_services'},
    (0x2f12,): {'man_made': 'tower', 'tower:type': 'communication'},
    (0x2f13,): {'services': 'repair'},
    (0x2f14,): {'services': 'social'},
    (0x2F15,): {'services': 'social'},
    (0x2f17,): {'highway': 'bus_stop'},
    # Government خدمات حكومية
    (0x3000,): {'amenity': 'townhall'},
    (0x3001,): {'amenity': 'police'},
    (0x3002,): {'amenity': 'hospital'},
    (0x3003,): {'xxx': 'xxx'},
    (0x3004,): {'amenity': 'courthouse'},
    (0x3005,): {'office': 'charity'},
    (0x3006,): {'barrier': 'border_control'},
    (0x3007,): {'amenity': 'public_building'},
    (0x3008,): {'amenity': 'fire_station'},
    (0x3A03,): {'amenity': 'place_of_worship'},
    (0x4100,): {'leisure': 'fishing'},
    (0x4200,): {'historic': 'wreck'},
    (0x4300,): {'amenity': 'ferry_terminal'},
    (0x4301,): {'shop': 'mall'},
    (0x4302,): {'xxx': 'xxx'},
    (0x4400,): {'amenity': 'fuel'},
    (0x4500,): {'amenity': 'restaurant'},
    (0x4600,): {'amenity': 'pub'},
    (0x4700,): {'leisure': 'slipway'},
    (0x4800,): {'tourism': 'campsite'},
    (0x4900,): {'leisure': 'park'},
    # (0x4a00,): {'tourism': 'picnic_site'},
    (0x4a00,): {'place': 'locality'},
    (0x4b00,): {'amenity': 'hospital'},
    (0x4c00,): {'tourism': 'information'},
    (0x4d00,): {'amenity': 'parking'},
    (0x4e00,): {'amenity': 'toilets'},
    (0x4e01,): {'xxx': 'xxx'},
    (0x4e02,): {'xxx': 'xxx'},
    (0x4e03,): {'xxx': 'xxx'},
    (0x4f00,): {'shop': 'beauty'},
    (0x4f07,): {'traffic': 'no_transit_sign'},
    (0x5000,): {'amenity': 'drinking_water'},
    (0x5001,): {'amenity': 'hospital'},
    (0x5002,): {'amenity': 'hospital'},
    (0x5004,): {'office': 'diplomatic'},
    (0x5100,): {'amenity': 'telephone'},
    (0x5200,): {'tourism': 'viewpoint'},
    (0x5400,): {'sport': 'swimming'},
    (0x5500,): {'waterway': 'dam'},
    (0x5700,): {'military': 'danger_area'},
    (0x5800,): {'noexit': 'yes'},
    (0x5900,): {'aeroway': 'aerodrome'},
    (0x5901,): {'aeroway': 'aerodrome'},
    (0x5902,): {'aeroway': 'aerodrome'},
    (0x5903,): {'aeroway': 'aerodrome'},
    (0x5904,): {'aeroway': 'helipad'},
    (0x5905,): {'aeroway': 'aerodrome'},
    (0x5a00,): {'distance_marker': 'yes'},
    (0x5a02,): {'xxx': 'xxx'},
    (0x5a04,): {'xxx': 'xxx'},
    (0x5a08,): {'xxx': 'xxx'},
    (0x5a09,): {'xxx': 'xxx'},
    (0x5e00,): {'place': 'locality'},
    (0x6100,): {'building': 'yes '},
    (0x6200,): {'peak': 'yes'},
    (0x6300,): {'man_made': 'survey_point'},
    # Man Made منشآت
    (0x6400,): {'highway': 'gate'},
    # (0x6400,): {'historic': 'ruins'},
    (0x6401,): {'bridge': 'yes'},
    (0x6402,): {'building': 'yes'},
    (0x6403,): {'landuse': 'cemetery'},
    (0x6404,): {'amenity': 'place_of_worship'},
    (0x6405,): {'amenity': 'public_building'},
    (0x6406,): {'highway': 'crossing'},
    (0x6407,): {'waterway': 'dam'},
    (0x6408,): {'amenity': 'hospital'},
    (0x6409,): {'waterway': 'dam'},
    (0x640a,): {'place': 'locality'},
    (0x640b,): {'military': 'barraks'},
    (0x640c,): {'man_made': 'mineshaft'},
    (0x640d,): {'man_made': 'pumping_rig'},
    (0x640e,): {'leisure': 'park'},
    (0x640f,): {'amenity': 'post_office'},
    (0x6410,): {'amenity': 'school'},
    (0x6411,): {'man_made': 'tower'},
    (0x6412,): {'highway': 'trailhead'},
    (0x6413,): {'tunnel': 'yes'},
    (0x6414,): {'man_made': 'water_well'},
    (0x6415,): {'place': 'locality'},
    (0x6416,): {'place': 'locality'},
    # HydroGraphics أماكن مائية
    (0x6500,): {'place': 'locality'},
    (0x6501,): {'waterway': 'stream'},
    (0x6502,): {'natural': 'dune'},
    (0x6503,): {'natural': 'water'},
    (0x6504,): {'natural': 'water'},
    (0x6505,): {'waterway': 'canal'},
    (0x6506,): {'waterway': 'canal'},
    (0x6507,): {'natural': 'water'},
    (0x6508,): {'waterway': 'waterfall'},
    (0x6509,): {'natural': 'gayser'},
    (0x650a,): {'natural': 'glacier'},
    (0x650b,): {'natural': 'water'},
    (0x650c,): {'natural': 'island'},
    (0x650d,): {'natural': 'water'},
    (0x650e,): {'waterway': 'rapid'},
    (0x650f,): {'landuse': 'reservoir'},
    (0x6511,): {'natural': 'spring'},
    (0x6512,): {'waterway': 'stream'},
    (0x6513,): {'waterway': 'wetland'},
    # Land features أماكن طبيعية
    (0x6600,): {'place': 'locality'},
    (0x6601,): {'natural': 'cave_entrance'},
    (0x6602,): {'place': 'locality'},
    (0x6603,): {'natural': 'basin'},
    (0x6604,): {'natural': 'dune'},
    (0x6605,): {'natural': 'bench'},
    (0x6606,): {'natural': 'cape'},
    (0x6607,): {'natural': 'cave_entrance'},
    (0x6608,): {'natural': 'sinkhole'},
    (0x6609,): {'natural': 'wetland'},
    (0x660a,): {'natural': 'wood'},
    (0x660b,): {'natural': 'gap'},
    (0x660c,): {'natural': 'gut'},
    (0x660d,): {'natural': 'isthmus'},
    (0x660e,): {'natural': 'lava'},
    (0x660f,): {'man_made': 'cairn'},
    (0x6610,): {'natural': 'scrub'},
    (0x6611,): {'natural': 'range'},
    (0x6612,): {'natural': 'reserve'},
    (0x6613,): {'natural': 'ridge'},
    (0x6614,): {'natural': 'peak'},
    (0x6615,): {'natural': 'slope'},
    (0x6616,): {'natural': 'peak'},
    (0x6617,): {'natural': 'valley'},
    (0x6618,): {'natural': 'wood'},
    (0x680a,): {'amenity': 'fuel'},
    #باصات وأماكن أخرى
    (0xf001,): {'amenity': 'bus_station'},
    (0xf001,): {'highway': 'bus_stop'},
    (0xf002,): {'highway': 'bus_stop'},
    (0xf003,): {'highway': 'bus_stop'},
    (0xf004,): {'highway': 'bus_stop'},
    (0xf006,): {'railway': 'halt'},
    (0xf007,): {'railway': 'station'},
    (0xf104,): {'amenity': 'place_of_worship'},
    (0xf201,): {'highway': 'traffic_signals'},
    (0xf306,): {'railway': 'level_crossing'},
    (0xf504,): {'amenity': 'university'}
}
## الخطوط والطرق
# POLYLINES
POLYLINE_TAG_MAP = {
    # طرق غير مصنفة
    (0x0000,): {'highway': 'road'},
    # major highway طرق رئيسية
    (0x0001,): {'highway': 'motorway'},
    # principal طرق أولية
    (0x0002,): {'highway': 'primary'},
    # Other hw طرق ثانوية
    (0x0003,): {'highway': 'secondary'},
    (0x0004,): {'highway': 'secondary'},
    # collector road طرق ثالثية
    (0x0005,): {'highway': 'tertiary'},
    # residantial طرق سكنية
    (0x0006,): {'highway': 'residential'},
    # alley/private ممرات وطرق سكنية
    (0x0007,): {'highway': 'residential'},
    # hw ramp low speed وصلات طرق
    (0x0008,): {'highway': 'primary_link'},
    (0x0009,): {'highway': 'trunk_link'},
    # unpaved طرق غير معبدة
    (0x000a,): {'highway': 'track'},
    # major hw connector وصلات طرق ثانوية
    (0x000b,): {'highway': 'secondary'},
    # roundabout دوارات
    (0x000c,): {'junction': 'roundabout'},
    # طرق غير مصنفة
    (0x000d,): {'highway': 'road'},
    (0x000e,): {'highway': 'road'},
    (0x000f,): {'highway': 'road'},
    (0x0010,): {'highway': 'road'},
    (0x0011,): {'railway': 'platform'},
    (0x0012,): {'highway': 'service'},
    (0x0013,): {'highway': 'steps'},
    # RAILROAD طرق قطارات
    (0x0014,): {'railway': 'rail'},
    # coastline خط الساحل
    (0x0015,): {'natural': 'coastline'},

    # walkway طرق مشي
    (0x0016,): {'highway': 'footway'},
    (0x0017,): {'barrier': 'fence'},
    (0x0018,): {'waterway': 'river'},
    (0x001a,): {'route': 'ferry'},
    (0x001b,): {'route': 'ferry'},

    # boundary state/province حدود وحواجز
    (0x001c,): {'barrier': 'fence'},
    # county حدود إدارية
    (0x001d,): {'boundary': 'administrative'},
    # international boundary حدود دولية
    (0x001e,): {'boundary': 'administrative'},
    # خطوط أخرى مثل الوديان والجيلان وغيرها
    (0x001f,): {'waterway': 'river'},
    (0x0021,): {'natural': 'cliff'},
    (0x0026,): {'waterway': 'stream'},
    (0x0027,): {'aeroway': 'runway'},
    (0x0028,): {'man_made': 'pipeline'},
    (0x0029,): {'power': 'line'},
    (0x0030,): {'sport': 'running', 'leisure': 'track'},
    (0x003f,): {'railway': 'subway'},
    (0x0042,): {'highway': 'unsurfaced'},
    (0x0044,): {'waterway': 'drain'},
    (0x0045,): {'boundary': 'administrative'},
    (0x0046,): {'barrier': 'fence'},
    (0x0048,): {'highway': 'pedestrian'},
    (0x0049,): {'highway': 'living_street'}
}
## المضلعات والمساحات
# POLYGONES
POLYGON_TAG_MAP = {
    (0x0,): {'xxx': 'xxx'},
    (0x0001,): {'landuse': 'residential'},
    (0x0002,): {'landuse': 'residential'},
    (0x0003,): {'landuse': 'millitary'},
    (0x0004,): {'landuse': 'millitary'},
    (0x0005,): {'amenity': 'parking'},
    (0x0006,): {'amenity': 'parking'},
    (0x0007,): {'landuse': 'nature_reserve'},
    (0x0008,): {'landuse': 'retail'},
    (0x0009,): {'building': 'yes'},
    (0x000a,): {'natural': 'wetland'},
    (0x000b,): {'building': 'hospital'},
    (0x000c,): {'landuse': 'industrial'},
    (0x000d,): {'natural': 'wood'},
    (0x000e,): {'aeroway': 'helipad'},
    (0x000f,): {'landuse': 'commercial'},
    (0x0010,): {'building': 'yes'},
    (0x0012,): {'landuse': 'quarry'},
    (0x0013,): {'building': 'yes'},
    (0x0014,): {'natural': 'scrub'},
    (0x0015,): {'natural': 'scrub'},
    (0x0016,): {'boundary': 'national_park'},
    (0x0017,): {'leisure': 'park'},
    (0x0018,): {'leisure': 'pitch'},
    (0x0019,): {'leisure': 'pitch'},
    (0x001a,): {'landuse': 'cemetery'},
    (0x001c,): {'landuse': 'grass'},
    (0x001e,): {'natural': 'wood'},
    (0x001f,): {'natural': 'wood'},
    (0x0020,): {'natural': 'wood'},
    (0x0021,): {'natural': 'wood'},
    (0x0022,): {'landuse': 'commercial'},
    (0x0023,): {'amenity': 'public_building'},
    (0x0024,): {'man_made': 'breakwater'},
    (0x0025,): {'man_made': 'pier'},
    (0x0028,): {'natural': 'water'},
    (0x0029,): {'natural': 'wetland'},
    (0x002c,): {'landuse': 'grass'},
    (0x002e,): {'landuse': 'beach'},
    (0x002f,): {'xxx': 'xxx'},
    (0x0032,): {'natural': 'water'},
    (0x003a,): {'aeroway': 'apron'},
    (0x003b,): {'natural': 'water'},
    (0x003c,): {'natural': 'water'},
    (0x003d,): {'natural': 'water'},
    (0x003f,): {'natural': 'water'},
    (0x0040,): {'natural': 'water'},
    (0x0041,): {'natural': 'wetland'},
    (0x0042,): {'natural': 'water'},
    (0x0043,): {'natural': 'water'},
    (0x0044,): {'natural': 'water'},
    (0x0045,): {'natural': 'water'},
    (0x0046,): {'natural': 'wetland'},
    (0x0047,): {'natural': 'water'},
    (0x0048,): {'natural': 'water'},
    (0x0049,): {'natural': 'water'},
    (0x004b,): {'xxx': 'xxx'},
    (0x004c,): {'natural': 'wetland'},
    (0x004e,): {'landuse': 'farmland'},
    (0x004f,): {'natural': 'scrub'},
    (0x0050,): {'leisure': 'nature_reserve'},
    (0x0051,): {'natural': 'marsh'},
    (0x0052,): {'landuse': 'forest'},
    (0x0053,): {'natural': 'wetland'},
    (0x005c,): {'natural': 'sand'},
    (0x005d,): {'landuse': 'orchard'},
    (0x005f,): {'amenity': 'place_of_worship', 'building': 'yes'},
    (0x006a,): {'building': 'train_station'},
    (0x006c,): {'building': 'yes'},
    (0x006d,): {'natural': 'wetland'},
    (0x006e,): {'amenity': 'public_building'},
    (0x006f,): {'amenity': 'public_building'},
    (0x0070,): {'shop': 'mall'},
    (0x0073,): {'natural': 'sand'},
    (0x007b,): {'leisure': 'nature_reserve'},
    (0x007e,): {'amenity': 'public_building'},
    (0x0081,): {'landuse': 'forest'},
    (0x0082,): {'landuse': 'forest'},
    (0x0083,): {'landuse': 'forest'},
    (0x0084,): {'landuse': 'forest'},
    (0x0085,): {'landuse': 'forest'},
    (0x0086,): {'leisure': 'garden'},
    (0x0087,): {'leisure': 'garden'},
    (0x0088,): {'leisure': 'garden'},
    (0x0089,): {'natural': 'sand'},
    (0x008a,): {'natural': 'bare_rock'},
    (0x008b,): {'natural': 'marsh'},
    (0x008f,): {'landuse': 'forest'},
    (0x0090,): {'landuse': 'forest'},
    (0x0091,): {'landuse': 'forest'},
    (0x0096,): {'natural': 'marsh'},
    (0x0098,): {'landuse': 'farmland'},
    (0x2d0a,): {'leisure': 'sports_centre'},
    (0x3002,): {'amenity': 'hospital'},
    (0x6402,): {'building': 'yes'},
    (0x6408,): {'building': 'clinic'}
}


# (دالة تنظيف التسميات)
def clean_label(label):
    codestart = label.find('~[')
    if codestart != -1:
        codeend = label.find(']', codestart)
        if codeend != -1:
            label = label[0:codestart] + ' ' + label[codeend + 1:]
    return label.strip().title()
    pass
def make_valid(geometry):
    if not geometry.is_valid:
        return geometry.buffer(0)
    return geometry
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP files", "*.mp"), ("All files", "*.*")])
    if file_path:
        input_file_var.set(file_path)


def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".osm",
                                             filetypes=[("OSM files", "*.osm"), ("All files", "*.*")])
    if file_path:
        output_file_var.set(file_path)


def start_conversion():
    input_file = input_file_var.get()
    output_file = output_file_var.get()
    do_dissolve = dissolve_var.get()

    if not input_file or not output_file:
        messagebox.showerror("Error", texts[current_language]["select_files_error"])
        return

    progress_var.set(0)
    progress_bar.start()

    try:
        convert_mp_to_osm(input_file, output_file, do_dissolve)
        compare_types(input_file)
        messagebox.showinfo("Success تم!", texts[current_language]["conversion_success"])
    except Exception as e:
        messagebox.showerror("Error خطأ", texts[current_language]["conversion_error"] + str(e))

    progress_bar.stop()
    progress_var.set(100)


def read_mp(file_path):
    with open(file_path, 'r', encoding='latin-1', errors='replace') as file:
        data = file.read()

    polygons = []
    current_polygon = None
    lines = data.split('\n')
    start_line = 0
    polygons_info = []

    for i, line in enumerate(lines):
        if line.startswith('[POLYGON]'):
            current_polygon = {'Type': None, 'Label': '', 'Coordinates': {}, 'Data': [], 'EndLevel': None}
            start_line = i
        elif current_polygon is not None and line.startswith('Type='):
            current_polygon['Type'] = line.split('=')[1]
        elif current_polygon is not None and line.startswith('Label='):
            label = line.split('=')[1]
            current_polygon['Label'] = label if label else ''
        elif current_polygon is not None and line.startswith('EndLevel='):
            current_polygon['EndLevel'] = line.split('=')[1]
        elif current_polygon is not None and line.startswith('Data'):
            data_num = int(line[4])
            coords = line.split('=')[1].strip('()').split('),(')
            coordinates = [tuple(map(float, coord.split(','))) for coord in coords]
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])
            current_polygon['Coordinates'][data_num] = coordinates
            current_polygon['Data'].append(data_num)
        elif line.startswith('[END]') and current_polygon is not None:
            for data_num in current_polygon['Data']:
                polygon = Polygon(shell=current_polygon['Coordinates'][data_num])
                polygons.append(
                    {'geometry': polygon, 'Type': current_polygon['Type'], 'Label': current_polygon['Label'],
                     'Data': data_num, 'EndLevel': current_polygon['EndLevel']})
            polygons_info.append((start_line, i + 1))
            current_polygon = None

    if polygons:
        gdf = gpd.GeoDataFrame(polygons, crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(polygons)

    return gdf, data, polygons_info


def write_mp(dissolved_gdf, original_data, polygons_info, output_file):
    lines = original_data.split('\n')

    with open(output_file, 'w', encoding='latin-1') as file:
        polygon_index = 0
        for i, line in enumerate(lines):
            if polygon_index < len(polygons_info) and polygons_info[polygon_index][0] == i:
                if polygon_index < len(dissolved_gdf):
                    file.write(f"[POLYGON]\n")
                    file.write(f"Type={dissolved_gdf.iloc[polygon_index]['Type']}\n")

                    label = dissolved_gdf.iloc[polygon_index]['Label']
                    if label != 'Unnamed':
                        file.write(f"Label={label}\n")

                    end_level = dissolved_gdf.iloc[polygon_index]['EndLevel']
                    if end_level is not None:
                        file.write(f"EndLevel={end_level}\n")

                    polygons = []
                    if isinstance(dissolved_gdf.iloc[polygon_index].geometry, Polygon):
                        polygons = [dissolved_gdf.iloc[polygon_index].geometry]
                    elif isinstance(dissolved_gdf.iloc[polygon_index].geometry, MultiPolygon):
                        polygons = dissolved_gdf.iloc[polygon_index].geometry.geoms

                    for polygon in polygons:
                        coords = polygon.exterior.coords
                        coord_str = ','.join(f"({x},{y})" for x, y in coords)
                        data_num = dissolved_gdf.iloc[polygon_index]['Data']
                        file.write(f"Data{data_num}={coord_str}\n")

                        for interior in polygon.interiors:
                            inner_coords = interior.coords
                            inner_coord_str = ','.join(f"({x},{y})" for x, y in inner_coords)
                            file.write(f"Data{data_num}={inner_coord_str}\n")

                    file.write(f"[END]\n\n")
                polygon_index += 1
            elif polygon_index > 0 and polygons_info[polygon_index - 1][1] > i:
                continue
            else:
                file.write(line + '\n')


def dissolve_polygons(gdf):
    dissolved_polygons = []

    if 'geometry' not in gdf.columns:
        return gpd.GeoDataFrame(dissolved_polygons)

    for (label, type_, data_num), group in gdf.groupby(['Label', 'Type', 'Data']):
        group['geometry'] = group['geometry'].apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)
        merged = unary_union(group.geometry)
        if isinstance(merged, Polygon):
            merged = [merged]
        elif isinstance(merged, MultiPolygon):
            merged = list(merged.geoms)

        merged = [poly.buffer(0) for poly in merged]

        for poly in merged:
            dissolved_polygons.append(
                {'geometry': poly, 'Type': type_, 'Label': label if label != '' else 'Unnamed', 'Data': data_num,
                 'EndLevel': group['EndLevel'].iloc[0] if not group['EndLevel'].isnull().all() else None})

    if dissolved_polygons:
        return gpd.GeoDataFrame(dissolved_polygons, crs=gdf.crs)
    else:
        return gpd.GeoDataFrame(dissolved_polygons)


def process_layer(gdf, data_num):
    layer_gdf = gdf[gdf['Data'] == data_num]
    return dissolve_polygons(layer_gdf)


def process_layers_parallel(gdf, data_nums):
    with ThreadPoolExecutor() as executor:
        dissolved_gdfs = list(executor.map(process_layer, [gdf] * len(data_nums), data_nums))
    return dissolved_gdfs


def add_tags_and_label(element, typecode, label, elementtagmap):
    for codes, taglist in elementtagmap.items():
        if typecode in codes:
            for key, value in taglist.items():
                tag = ET.Element('tag', k=key, v=value)
                tag.tail = '\n    '
                element.append(tag)

    if label:
        name_tag = ET.Element('tag', k='name', v=str(label.strip().title()))
        name_tag.tail = '\n    '
        element.append(name_tag)
created_nodes = {}
def process_node(line_iterator, nodeid, elementtagmap):
    node = ET.Element('node', visible='true', id=str(nodeid))
    for line in line_iterator:
        if line.startswith('[END]'):
            break

        if line.startswith('Label'):
            label = clean_label(line.split('=')[1])
            tag = ET.Element('tag', k='name', v=label)
            tag.tail = '\n    '
            node.append(tag)

        if line.startswith('Type'):
            typecode = int(line.split('=')[1].strip(), 16)
            for codes, taglist in elementtagmap.items():
                if typecode in codes:
                    for key, value in taglist.items():
                        tag = ET.Element('tag', k=key, v=value)
                        tag.tail = '\n    '
                        node.append(tag)

        if line.startswith('Data0'):  # تعيين Data0 فقط
            coords = line.split('=')[1].strip().split(',')
            point = Point(float(coords[1][:-1]), float(coords[0][1:]))
            node.set('lat', str(point.y))
            node.set('lon', str(point.x))

    node.text = '\n    '
    node.tail = '\n  '
    return node
def process_polyline(line_iterator, nodeid, elementtagmap):
    global created_nodes
    rnodes = {}
    label = None
    typecode = None
    way_node = None

    for line_number, line in enumerate(line_iterator, start=1):
        if line.startswith('[END]'):
            break

        if line.startswith('Label'):
            label = clean_label(line.split('=')[1])

        if line.startswith('Type'):
            typecode = int(line.split('=')[1].strip(), 16)

        if line.startswith('Data0'):  # تعيين Data0 فقط
            coords = line.split('=')[1].strip().split(',')
            line_points = []

            for i in range(0, len(coords), 2):
                try:
                    lat = float(coords[i][1:])
                    lon = float(coords[i + 1][:-1])
                    line_points.append((lon, lat))
                except (IndexError, ValueError) as e:
                    log_message("error_converting_coords", line_number, coords[i], coords[i + 1] if i + 1 < len(coords) else "Missing")
                    continue

            if line_points:
                line_geom = LineString(line_points)
                way_node = ET.Element('way', visible='true', id=str(nodeid))
                nodeid -= 1

                for point in line_geom.coords:
                    point_tuple = (point[0], point[1])

                    if point_tuple in created_nodes:
                        curId = created_nodes[point_tuple]
                    else:
                        curId = nodeid
                        created_nodes[point_tuple] = curId
                        nodeid -= 1

                        node = ET.Element('node', visible='true', id=str(curId),
                                         lat=str(point[1]), lon=str(point[0]))
                        node.text = '\n    '
                        node.tail = '\n  '
                        osm.append(node)

                    nd = ET.Element('nd', ref=str(curId))
                    nd.tail = '\n    '
                    way_node.append(nd)

                add_tags_and_label(way_node, typecode, label, elementtagmap)
                osm.append(way_node)

    return nodeid


def process_polygon(line_iterator, nodeid, elementtagmap):
    global created_nodes
    rnodes = {}
    polygon_ways = []
    label = None
    typecode = None

    for line_number, line in enumerate(line_iterator, start=1):
        if line.startswith('[END]'):
            break

        if line.startswith('Label'):
            label = clean_label(line.split('=')[1])

        if line.startswith('Type'):
            typecode = int(line.split('=')[1].strip(), 16)

        if line.startswith('Data0'):
            coords = line.split('=')[1].strip().split(',')
            poly_points = []

            for i in range(0, len(coords), 2):
                try:
                    lat = float(coords[i][1:])
                    lon = float(coords[i + 1][:-1])
                    poly_points.append((lon, lat))
                except (IndexError, ValueError) as e:
                    log_message("error_converting_coords", line_number, coords[i],
                                coords[i + 1] if i + 1 < len(coords) else "Missing")
                    continue

            if poly_points:
                # Ensuring the polygon is closed
                if poly_points[0] != poly_points[-1]:
                    poly_points.append(poly_points[0])

                poly_geom = Polygon(poly_points)

                if not poly_geom.is_valid:
                    poly_geom = make_valid(poly_geom)
                    poly_geom = poly_geom.buffer(0)

                if isinstance(poly_geom, Polygon):
                    poly_geom = [poly_geom]
                elif isinstance(poly_geom, MultiPolygon):  
                    poly_geom = list(poly_geom.geoms)  
                else:
                    log_message("unexpected_geometry_type", type(poly_geom))
                    return [], nodeid, label, typecode

                for single_poly in poly_geom:
                    way_node = ET.Element('way', visible='true', id=str(nodeid))
                    nodeid -= 1

                    for point in single_poly.exterior.coords: 
                        point_tuple = (point[0], point[1])

                        if point_tuple in created_nodes:
                            curId = created_nodes[point_tuple]
                        else:
                            curId = nodeid
                            created_nodes[point_tuple] = curId
                            nodeid -= 1

                            node = ET.Element('node', visible='true', id=str(curId),
                                              lat=str(point[1]), lon=str(point[0]))
                            node.text = '\n    '
                            node.tail = '\n  '
                            osm.append(node)

                        nd = ET.Element('nd', ref=str(curId))
                        nd.tail = '\n    '
                        way_node.append(nd)

                    polygon_ways.append(way_node)

    return polygon_ways, nodeid, label, typecode
def create_multipolygon_relation(ways, relation_id, relation_label, relation_typecode):
    relation = ET.Element('relation', id=str(relation_id), version='1')
    relation.text = '\n    '
    relation.tail = '\n  '
    relation.append(ET.Element('tag', k='type', v='multipolygon'))
    add_tags_and_label(relation, relation_typecode, relation_label, POLYGON_TAG_MAP)

    for i, way in enumerate(ways):
        way.text = '\n    '
        way.tail = '\n  '
        osm.append(way)

        role = 'outer' if i == 0 else 'inner'
        member = ET.Element('member', type='way', ref=way.get('id'), role=role)
        member.tail = '\n    '
        relation.append(member)

    return relation


def convert_mp_to_osm(file_mp, file_osm, do_dissolve=True):
    global osm, nodeid, created_nodes 
    created_nodes = {} 

    if not os.path.isfile(file_mp):
        log_message("file_not_found", file_mp)
        return

    gdf, original_data, polygons_info = read_mp(file_mp)

    log_message("file_read_success")

    if do_dissolve and 'geometry' in gdf.columns and not gdf.empty:
        # معالجة المضلعات فقط في عملية الدمج
        polygons_gdf = gdf[gdf['geometry'].type.isin(['Polygon', 'MultiPolygon'])]

        if not polygons_gdf.empty:
            data_nums = polygons_gdf['Data'].unique()
            dissolved_gdfs = process_layers_parallel(polygons_gdf, data_nums)

            if dissolved_gdfs:
                final_dissolved_gdf = gpd.GeoDataFrame(pd.concat(dissolved_gdfs, ignore_index=True), crs=gdf.crs)
                final_dissolved_gdf['Label'] = final_dissolved_gdf['Label'].apply(lambda x: '' if x == 'Unnamed' else x)

                log_message("dissolve_success")
                output_dissolved_file = 'dissolved_file.mp'
                write_mp(final_dissolved_gdf, original_data, polygons_info, output_dissolved_file)
                log_message("merged_file_written", output_dissolved_file)
                file_mp = output_dissolved_file
            else:
                log_message("no_polygons_after_dissolve")
        else:
            log_message("no_polygons_to_dissolve")

    osm = ET.Element('osm', version='0.6', generator='mp2osm')
    osm.text = '\n  '
    osm.tail = '\n'
    nodeid = -1

    poi_counter = 0
    polyline_counter = 0
    polygon_counter = 0
    relation_counter = -1

    with open(file_mp, encoding='windows-1256') as f:
        lines = iter(f.readlines())
        for line in lines:
            if line.startswith(('[POI]', '[RGN10]', '[RGN20]')):
                nodeid -= 1
                osm.append(process_node(lines, nodeid, POI_TAG_MAP))
                poi_counter += 1

            elif line.startswith(('[POLYLINE]', '[RGN40]')):
                nodeid -= 1
                nodeid = process_polyline(lines, nodeid, POLYLINE_TAG_MAP)
                polyline_counter += 1

            elif line.startswith(('[POLYGON]', '[RGN80]')):
                nodeid -= 1
                polygon_ways, nodeid, label, typecode = process_polygon(lines, nodeid, POLYGON_TAG_MAP)
                polygon_counter += 1

                if len(polygon_ways) > 1:
                    relation = create_multipolygon_relation(polygon_ways, nodeid, label, typecode)
                    osm.append(relation)
                    nodeid -= 1
                else:
                    for way in polygon_ways:
                        add_tags_and_label(way, typecode, label, POLYGON_TAG_MAP)
                        osm.append(way)

    with open(file_osm, 'w', encoding='utf-8') as f:
        f.write('<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n')
        f.write(ET.tostring(osm, encoding='utf-8').decode('utf-8'))

    log_message("separator")
    log_message("conversion_totals_header")
    log_message("separator")
    log_message("num_pois", poi_counter)
    log_message("num_polylines", polyline_counter)
    log_message("num_polygons", polygon_counter)
    log_message("num_relations", relation_counter * -1)


def compare_types(file_mp):
    types_in_file_poi = set()
    types_in_file_polyline = set()
    types_in_file_polygon = set()

    current_section = None

    with open(file_mp, encoding='windows-1256') as f:
        for line in f:
            if line.startswith('[POI]'):
                current_section = 'POI'
            elif line.startswith('[POLYLINE]'):
                current_section = 'POLYLINE'
            elif line.startswith('[POLYGON]'):
                current_section = 'POLYGON'

            if line.startswith('Type'):
                typecode_str = line.split('=')[1].strip()
                if typecode_str.startswith("0x") and all(
                        c in "0123456789abcdefABCDEFx" for c in typecode_str
                ):
                    typecode = int(typecode_str, 16)
                    if current_section == 'POI':
                        types_in_file_poi.add(typecode)
                    elif current_section == 'POLYLINE':
                        types_in_file_polyline.add(typecode)
                    elif current_section == 'POLYGON':
                        types_in_file_polygon.add(typecode)

    defined_poi_types = set([code[0] for code in POI_TAG_MAP.keys()])
    missing_poi = types_in_file_poi - defined_poi_types
    log_message("separator")
    log_message("poi_types_analysis")
    log_message("separator")
    log_message("num_poi_types_file", file_mp, len(types_in_file_poi))
    log_message("num_poi_types_defined", len(defined_poi_types))
    log_message("num_missing_poi_types", len(missing_poi))
    log_message("missing_poi_types", ', '.join(hex(item) for item in missing_poi))

    defined_polyline_types = set([code[0] for code in POLYLINE_TAG_MAP.keys()])
    missing_polyline = types_in_file_polyline - defined_polyline_types
    log_message("separator")
    log_message("polyline_types_analysis")
    log_message("separator")
    log_message("num_polyline_types_file", file_mp, len(types_in_file_polyline))
    log_message("num_polyline_types_defined", len(defined_polyline_types))
    log_message("num_missing_polyline_types", len(missing_polyline))
    log_message("missing_polyline_types", ', '.join(hex(item) for item in missing_polyline))

    defined_polygon_types = set([code[0] for code in POLYGON_TAG_MAP.keys()])
    missing_polygon = types_in_file_polygon - defined_polygon_types
    log_message("separator")
    log_message("polygon_types_analysis")
    log_message("separator")
    log_message("num_polygon_types_file", file_mp, len(types_in_file_polygon))
    log_message("num_polygon_types_defined", len(defined_polygon_types))
    log_message("num_missing_polygon_types", len(missing_polygon))
    log_message("missing_polygon_types", ', '.join(hex(item) for item in missing_polygon))


# فهرس نصوص التطبيق
messages = {
    "ar": {
        "file_read_success": "تمت قراءة الملف بنجاح",
        "dissolve_success": "تمت عملية دمج المضلعات بنجاح",
        "merged_file_written": "تم كتابة الملف المدمج إلى \n'{}' للتحقق",
        "no_polygons_after_dissolve": "لم يتم العثور على مضلعات بعد عملية الدمج",
        "no_polygons_to_dissolve": "لا توجد مضلعات لدمجها",
        "file_not_found": "خطأ: الملف '{}' غير موجود",
        "conversion_totals": "======\nالإجماليات\n======",
        "num_pois": "عدد النقاط/نقاط الاهتمام POI: {}",
        "num_polylines": "عدد الخطوط POLYLINE: {}",
        "num_polygons": "عدد المضلعات POLYGON: {}",
        "num_relations": "عدد العلاقات: {}",
        "poi_types_analysis": "========================\n"
                              "تحليل أنواع النقاط\n"
                              "========================",
        "num_poi_types_file": "عدد أنواع النقاط في \n'{}': {}",
        "num_poi_types_defined": "عدد أنواع النقاط المعرفة في تطبيق التحويل: {}",
        "num_missing_poi_types": "عدد أنواع النقاط الغير معرفة في تطبيق التحويل: {}",
        "missing_poi_types": " بيان بأنواع النقاط الغير معرفة في تطبيق التحويل: {}",
        "polyline_types_analysis": "========================\n"
                                   "تحليل أنواع POLYLINE\n"
                                   "========================",
        "num_polyline_types_file": "عدد أنواع الخطوط في \n'{}': {}",
        "num_polyline_types_defined": "عدد أنواع الخطوط المعرفة في تطبيق التحويل: {}",
        "num_missing_polyline_types": "عدد أنواع الخطوط الغير معرفة في تطبيق التحويل: {}",
        "missing_polyline_types": "بيان بأنواع الخطوط الغير معرفة في تطبيق التحويل: {}",
        "polygon_types_analysis": "========================\n"
                                  "تحليل أنواع POLYGON\n"
                                  "========================",
        "num_polygon_types_file": "عدد أنواع المضلعات في \n'{}': {}",
        "num_polygon_types_defined": "عدد أنواع المضلعات المعرفة في تطبيق التحويل: {}",
        "num_missing_polygon_types": "عدد أنواع المضلعات الغير معرفة في تطبيق التحويل: {}",
        "missing_polygon_types": "بيان بأنواع المضلعات الغير معرفة في تطبيق التحويل: {}",
        "error_reading_coords": "خطأ في قراءة الإحداثيات: {}",
        "error_converting_coords": "خطأ في تحويل الإحداثيات إلى أرقام: {}, {}",
        "raw_coordinates": "الإحداثيات الخام عند السطر {}: {}",
        "separator": "========",
        "conversion_totals_header": "======\nالإجماليات\n======",
    },
    "en": {
        "file_read_success": "File read successfully",
        "dissolve_success": "Dissolve operation performed successfully",
        "merged_file_written": "The merged file was written to '{}' for verification",
        "no_polygons_after_dissolve": "No polygons found after dissolve operation",
        "no_polygons_to_dissolve": "No polygons to dissolve",
        "file_not_found": "Error: File '{}' not found",
        "conversion_totals": "======\nTotals\n======",
        "num_pois": "Number of POIs: {}",
        "num_polylines": "Number of POLYLINEs: {}",
        "num_polygons": "Number of POLYGONs: {}",
        "num_relations": "Number of RELATIONs: {}",
        "poi_types_analysis": "========================\n"
                              "Analysis of POI Types\n"
                              "========================",
        "num_poi_types_file": "Number of POI types in '{}': {}",
        "num_poi_types_defined": "Number of POI types defined in code: {}",
        "num_missing_poi_types": "Number of missing POI types from the file: {}",
        "missing_poi_types": "Missing POI Types from the file: {}",
        "polyline_types_analysis": "========================\n"
                                   "Analysis of POLYLINE Types\n"
                                   "========================",
        "num_polyline_types_file": "Number of POLYLINE types in '{}': {}",
        "num_polyline_types_defined": "Number of POLYLINE types defined in code: {}",
        "num_missing_polyline_types": "Number of missing POLYLINE types from the file: {}",
        "missing_polyline_types": "Missing POLYLINE Types from the file: {}",
        "polygon_types_analysis": "========================\n"
                                  "Analysis of POLYGON Types\n"
                                  "========================",
        "num_polygon_types_file": "Number of POLYGON types in '{}': {}",
        "num_polygon_types_defined": "Number of POLYGON types defined in code: {}",
        "num_missing_polygon_types": "Number of missing POLYGON types from the file: {}",
        "missing_polygon_types": "Missing POLYGON Types from the file: {}",
        "error_reading_coords": "Error reading coordinates: {}",
        "error_converting_coords": "Error converting coordinates to numbers: {}, {}",
        "raw_coordinates": "Raw coordinates at line {}: {}",
        "separator": "========",
        "conversion_totals_header": "======\nTotals\n======",
    }
}


def log_message(message_key, *args):
    message = messages[current_language][message_key].format(*args)
    text_area.config(state=tk.NORMAL)

    if current_language == "ar":
        reshaped_message = arabic_reshaper.reshape(message)
        bidi_message = get_display(reshaped_message)
        text_area.insert(tk.END, bidi_message + '\n', "rtl")
    else:
        text_area.insert(tk.END, message + '\n')

    text_area.config(state=tk.DISABLED)
    text_area.see(tk.END)

# إعداد النصوص للغتين
texts = {
    "ar": {
        "input_file_label": "ملف MP المدخل:",
        "output_file_label": "ملف OSM المخرج:",
        "browse_button": "تصفح",
        "start_conversion_button": "ابدأ التحويل",
        "dissolve_option": "تمكين الدمج",
        "language_button": "Switch to English",
        "select_files_error": "الرجاء تحديد ملفات الإدخال والإخراج.",
        "conversion_success": "تم إكمال التحويل بنجاح!",
        "conversion_error": "حدث خطأ أثناء التحويل:",
    },
    "en": {
        "input_file_label": "Input MP File:",
        "output_file_label": "Output OSM File:",
        "browse_button": "Browse",
        "start_conversion_button": "Start Conversion",
        "dissolve_option": "Enable Dissolve",
        "language_button": "تبديل إلى العربية",
        "select_files_error": "Please select input and output files.",
        "conversion_success": "Conversion completed successfully!",
        "conversion_error": "An error occurred during conversion:",
    }
}

current_language = "ar"  # اللغة الافتراضية


def update_language(lang):
    global current_language
    current_language = lang

    # إعادة تشكيل النصوص للعرض الصحيح
    reshaped_input = arabic_reshaper.reshape(texts[lang]["input_file_label"])
    reshaped_output = arabic_reshaper.reshape(texts[lang]["output_file_label"])
    reshaped_dissolve = arabic_reshaper.reshape(texts[lang]["dissolve_option"])
    reshaped_start = arabic_reshaper.reshape(texts[lang]["start_conversion_button"])
    reshaped_browse = arabic_reshaper.reshape(texts[lang]["browse_button"])
    reshaped_language = arabic_reshaper.reshape(texts[lang]["language_button"])

    # تحديث النصوص في الواجهة
    input_file_label.config(text=get_display(reshaped_input), anchor="e" if lang == "ar" else "w")
    output_file_label.config(text=get_display(reshaped_output), anchor="e" if lang == "ar" else "w")
    browse_input_button.config(text=get_display(reshaped_browse))
    browse_output_button.config(text=get_display(reshaped_browse))
    start_button.config(text=get_display(reshaped_start))
    dissolve_checkbutton.config(text=get_display(reshaped_dissolve))
    language_button.config(text=get_display(reshaped_language))

    if lang == "ar":
        # محاذاة من اليمين لليسار
        input_file_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
        input_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_input_button.grid(row=0, column=0, padx=10, pady=5)

        output_file_label.grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)
        output_entry.grid(row=1, column=1, padx=10, pady=5)
        browse_output_button.grid(row=1, column=0, padx=10, pady=5)

        dissolve_checkbutton.grid(row=2, column=1, padx=10, pady=5)
        start_button.grid(row=3, column=1, padx=10, pady=10)
        language_button.grid(row=3, column=0, padx=10, pady=10, columnspan=3, sticky=tk.W)
    else:
        # محاذاة من اليسار لليمين
        input_file_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        input_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_input_button.grid(row=0, column=2, padx=10, pady=5)

        output_file_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        output_entry.grid(row=1, column=1, padx=10, pady=5)
        browse_output_button.grid(row=1, column=2, padx=10, pady=5)

        dissolve_checkbutton.grid(row=2, column=1, padx=10, pady=5)
        start_button.grid(row=3, column=1, padx=10, pady=10)
        language_button.grid(row=3, column=2, padx=10, pady=10, columnspan=3, sticky=tk.E)


# في إعداد الواجهة (بداية تعريف عناصر واجهة المستخدم)
app = tk.Tk()
app.title("MP Converter محول ام بي")

input_file_var = tk.StringVar()
output_file_var = tk.StringVar()
dissolve_var = tk.BooleanVar()

input_file_label = tk.Label(app, text=texts[current_language]["input_file_label"], anchor="e")
input_file_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

input_entry = tk.Entry(app, textvariable=input_file_var, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)

browse_input_button = tk.Button(app, text=texts[current_language]["browse_button"], command=select_input_file)
browse_input_button.grid(row=0, column=2, padx=10, pady=5)

output_file_label = tk.Label(app, text=texts[current_language]["output_file_label"], anchor="e")
output_file_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

output_entry = tk.Entry(app, textvariable=output_file_var, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)

browse_output_button = tk.Button(app, text=texts[current_language]["browse_button"], command=select_output_file)
browse_output_button.grid(row=1, column=2, padx=10, pady=5)

dissolve_checkbutton = tk.Checkbutton(app, text=texts[current_language]["dissolve_option"], variable=dissolve_var)
dissolve_checkbutton.grid(row=2, column=1, padx=10, pady=5)

start_button = tk.Button(app, text=texts[current_language]["start_conversion_button"], command=start_conversion)
start_button.grid(row=3, column=1, padx=10, pady=10)

language_button = tk.Button(app, text=texts[current_language]["language_button"],
                            command=lambda: update_language("en" if current_language == "ar" else "ar"))
language_button.grid(row=3, column=2, padx=10, pady=10, columnspan=3, sticky=tk.E)

progress_var = tk.IntVar()
progress_bar = Progressbar(app, variable=progress_var, maximum=100)
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="we")

text_area = scrolledtext.ScrolledText(app, state=tk.DISABLED, width=60, height=15)
text_area.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
text_area.tag_configure("rtl", justify=tk.RIGHT)
update_language(current_language)

app.mainloop()
