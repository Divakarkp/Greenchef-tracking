# app/utils.py

import barcode
from barcode.writer import ImageWriter
import os

def generate_barcode(box_code):
    if not os.path.exists("app/barcodes"):
        os.makedirs("app/barcodes")
    
    code128 = barcode.get_barcode_class('code128')
    barcode_obj = code128(box_code, writer=ImageWriter())

    filepath = f"app/barcodes/{box_code}"
    barcode_obj.save(filepath)
    
    return f"/barcodes/{box_code}.png"
