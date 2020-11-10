import base64

import numpy as np
import pandas as pd

from datetime import date


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. txt_out.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" \
              download="{download_filename}">{download_link_text}</a>'


def today():
    return str(date.today())

def wrap_text(text, max_char):
    if len(text) < max_char:
        return text
    else:
        split_name = text.split(' ')
        pointer = 0
        combined_str = ''
        current_str = ''
        while pointer < len(split_name):
            if (len(split_name[pointer]) > max_char) and (len(current_str) == 0):
                combined_str = combined_str + '\n' + split_name[pointer]
            elif (len(split_name[pointer]) > max_char) and (len(current_str) != 0):
                combined_str = combined_str + '\n' + current_str
                combined_str = combined_str + '\n' + split_name[pointer]
            elif len(split_name[pointer]) + len(current_str) > max_char:
                combined_str = combined_str + '\n' + current_str
                current_str = split_name[pointer]
            else:
                current_str = current_str + split_name[pointer] + ' '
            pointer += 1
        combined_str = combined_str + '\n' + current_str
        return combined_str


