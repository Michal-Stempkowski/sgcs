"""
For generating plant wsd files with different levels of accurancy
"""

import os
import sys
import time

import subprocess

DIAG_FOLDER_NAME = ''
IN_FILE_EXT = '.ui'
OUT_FILE_EXT = '.py'
GEN_SUFF = '__gen'


def get_script_path():
    """
    Returns folder in which the script is placed
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dest_filename(filename):
    """
    Returns well-formated destination file's filenam
    """
    return filename.replace(IN_FILE_EXT, GEN_SUFF + OUT_FILE_EXT)


def dest_absolute_path(diag_folder_path, filename):
    """
    Returns destination file's absolute path
    """
    return os.path.join(diag_folder_path, dest_filename(filename))


def perform_filtering(folder, filename):
    """
    Preforms filtering for single filter/file
    """
    input = os.path.join(folder, filename)
    output = dest_absolute_path(folder, filename)
    subprocess.call(' '.join(['pyuic4.bat', '-x', input, '-o', output]))


def main():
    """
    Main function
    """

    diag_folder_path = os.path.join(get_script_path(), DIAG_FOLDER_NAME)

    update_dict = dict()
    for filename in os.listdir(diag_folder_path):
        full_name = os.path.join(diag_folder_path, filename)
        update_dict[full_name] = os.path.getmtime(full_name)

    while True:
        for filename in os.listdir(diag_folder_path):
            # print(filename)
            if filename.endswith(IN_FILE_EXT) and GEN_SUFF not in filename:
                # print(filename)
                mod_time = os.path.getmtime(filename)
                if filename not in update_dict or mod_time > update_dict[filename]:
                    # print(filename)
                    full_name = os.path.join(diag_folder_path, filename)
                    update_dict[filename] = mod_time
                    perform_filtering(diag_folder_path, filename)

        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('finished!')

