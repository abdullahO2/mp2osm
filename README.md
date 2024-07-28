# محول ام بي (MP Converter)

[![LICENSE](https://img.shields.io/badge/license-GPL%20V2%20or%20later-green)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

## مقدمة (Introduction)

هذا الكود هو أداة تحويل مبسطة من صيغة ملفات الخرائط MapPoint (.mp) إلى صيغة ملفات OpenStreetMap (.osm) مفتوحة المصدر. 

**مميزات هذا الإصدار:**

* واجهة مستخدم رسومية بسيطة لسهولة الاستخدام.
* دعم اللغتين العربية والإنجليزية.
* خيار دمج المضلعات المتداخلة.
* تحليل لأنواع العناصر الموجودة في ملف .mp ومقارنتها مع الأنواع المُعرّفة في الكود.

**مصدر الكود الأصلي:**

تم تعديل هذا الكود من كود "mp2osm_catmp.py" الموجود في مستودع OpenStreetMap SVN:

[https://github.com/openstreetmap/svn-archive/tree/main/applications/utils/import/mp2osm](https://github.com/openstreetmap/svn-archive/tree/main/applications/utils/import/mp2osm)

## أبرز التعديلات:

* إضافة واجهة مستخدم رسومية (GUI) باستخدام مكتبة Tkinter.
* دعم اللغتين العربية والإنجليزية في واجهة المستخدم.
* إضافة خيار دمج المضلعات باستخدام Geopandas.
* تحسين عملية قراءة وتحليل ملفات .mp.
* تحليل لأنواع العناصر (POI, POLYLINE, POLYGON) في ملف .mp.
* مقارنة أنواع العناصر في ملف .mp مع الأنواع المُعرّفة في الكود وتسجيل أي أنواع مفقودة.

## متطلبات التشغيل (Requirements)

* Python 3.x
* مكتبات Python التالية:
    * tkinter
    * geopandas
    * pandas
    * shapely
    * xml.etree.ElementTree
    * os
    * concurrent.futures
    * bidi
    * arabic_reshaper

## طريقة الاستخدام (Usage)

1.  تأكد من تثبيت Python 3.x والمكتبات المطلوبة.
2.  قم بتشغيل البرنامج النصي `mo2U3.py`.
3.  حدد ملف .mp المدخل باستخدام زر "Browse".
4.  حدد ملف .osm المخرج باستخدام زر "Browse".
5.  (اختياري) حدد "Enable Dissolve" لدمج المضلعات المتداخلة.
6.  اضغط على زر "Start Conversion" لبدء عملية التحويل.

## ملاحظات:

* قد تستغرق عملية التحويل بعض الوقت اعتمادًا على حجم ملف .mp.
* سيتم عرض تفاصيل عملية التحويل في منطقة النص في واجهة المستخدم الرسومية.
* سيتم إنشاء ملف .osm المخرج في الموقع الذي حددته.

## الترخيص (License)

GPL V2 or later

---

# MP Converter

[![LICENSE](https://img.shields.io/badge/license-GPL%20V2%20or%20later-green)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

## Introduction

This code provides a simplified tool to convert MapPoint files (.mp) into the open-source OpenStreetMap (.osm) file format.

**Key Features of this version:**

* Simple graphical user interface (GUI) for ease of use.
* Support for both Arabic and English languages.
* Option to dissolve overlapping polygons.
* Analysis of feature types (POI, POLYLINE, POLYGON) in the .mp file.
* Comparison of feature types in the .mp file with those defined in the code, reporting any missing types.

**Original Code Source:**

This code is modified from "mp2osm_catmp.py" found in the OpenStreetMap SVN repository:

[https://github.com/openstreetmap/svn-archive/tree/main/applications/utils/import/mp2osm](https://github.com/openstreetmap/svn-archive/tree/main/applications/utils/import/mp2osm)

## Notable Modifications:

* Implementation of a graphical user interface (GUI) using Tkinter.
* Bilingual support (Arabic and English) for the user interface.
* Addition of a polygon dissolve option using Geopandas.
* Enhancements to .mp file reading and parsing.
* Analysis of feature types (POI, POLYLINE, POLYGON) in the .mp file.
* Comparison of feature types in the .mp file with those defined in the code, with logging of missing types.

## Requirements:

* Python 3.x
* The following Python libraries:
    * tkinter
    * geopandas
    * pandas
    * shapely
    * xml.etree.ElementTree
    * os
    * concurrent.futures
    * bidi
    * arabic_reshaper

## Usage:

1.  Ensure Python 3.x and the required libraries are installed.
2.  Run the script `mo2U3.py`.
3.  Select the input .mp file using the "Browse" button.
4.  Select the output .osm file using the "Browse" button.
5.  (Optional) Check "Enable Dissolve" to merge overlapping polygons.
6.  Click the "Start Conversion" button to initiate the conversion process.

## Notes:

* The conversion process may take some time depending on the size of the .mp file.
* Conversion details will be displayed in the text area of the GUI.
* The output .osm file will be created at the specified location.

## License:

GPL V2 or later
