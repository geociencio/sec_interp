import xml.etree.ElementTree as ET

tree = ET.parse("i18n/SecInterp_es.ts")
root = tree.getroot()
for msg in root.iter("message"):
    source = msg.find("source").text
    if source and "Please check the logs" in source:
        print(repr(source))
