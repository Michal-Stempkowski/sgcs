"""
For generating plant wsd files with different levels of accurancy
"""

import os
import sys
import time

DIAG_FOLDER_NAME = 'diagrams'
FILE_EXT = '.wsd'
GEN_SUFF = '__gen'


class Filter(object):
    """docstring for Filter"""
    def __init__(self, name, words):
        super(Filter, self).__init__()
        self.name = name
        self.words = words
        self.omit_next = False

    def filter(self, line):
        """Performs generation of filtered plant"""
        if any(word in line for word in self.words):
            self.omit_next = True
            return ''
        elif self.omit_next:
            self.omit_next = False
            return ''

        return line


class InlineFilter(object):
    """docstring for InlineFilter"""
    def __init__(self, name, ommited):
        super(InlineFilter, self).__init__()
        self.ommited = ommited
        self.name = name

    def filter(self, line):
        """Performs generation of filtered plant"""
        return line if self.ommited not in line else ''


class OrFilter(object):
    """docstring for OrFilter"""
    def __init__(self, name, *args):
        super(OrFilter, self).__init__()
        self.name = name
        self.args = args

    def filter(self, line):
        """Performs generation of filtered plant"""
        result = line
        for fil in self.args:
            result = fil.filter(result)
            if result:
                return result

        return ''


class AndFilter(object):
    """docstring for AndFilter"""
    def __init__(self, name, *args):
        super(AndFilter, self).__init__()
        self.args = args
        self.name = name

    def filter(self, line):
        """Performs generation of filtered plant"""
        result = line
        for fil in self.args:
            result = fil.filter(result)
            if not result:
                return ''

        return result


class ZoomOutFilter(object):
    begin_token = '&begin_'
    end_token = '&end_'
    alternative_token = '&alt_'

    """docstring for ZoomOutFilter"""
    def __init__(self, name, magic_word):
        super(ZoomOutFilter, self).__init__()
        self.name = name
        self.magic_word = magic_word
        self.in_zone = False
        self.magic_start = ZoomOutFilter.begin_token + self.magic_word
        self.magic_end = ZoomOutFilter.end_token + self.magic_word
        self.magic_alt = ZoomOutFilter.alternative_token + self.magic_word

    def filter(self, line):
        """Performs generation of filtered plant"""
        if self.magic_start in line:
            self.in_zone = True
        elif self.magic_end in line:
            self.in_zone = False
        else:

            if self.magic_alt in line:
                return line.replace("'", "").replace(self.magic_alt, '')
            elif self.in_zone:
                return ''
            else:
                return line


def get_filters():
    """
    Returns fresh filter list
    """

    lean = InlineFilter('lean1', '..')
    h1 = ZoomOutFilter('h1', 'cyk_executors')
    AndFilter('h1', ZoomOutFilter('h1', 'cyk_executors'))

    return [
        lean,
        Filter('de', ['&dependency_executors']),
        h1,
        AndFilter('h1_lean', lean, h1)]


def get_script_path():
    """
    Returns folder in which the script is placed
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dest_filename(filename, fil):
    """
    Returns well-formated destination file's filenam
    """
    return filename.replace(FILE_EXT, fil.name + GEN_SUFF + FILE_EXT)


def dest_absolute_path(diag_folder_path, filename, fil):
    """
    Returns destination file's absolute path
    """
    return os.path.join(diag_folder_path, dest_filename(filename, fil))


def perform_filtering(folder, filename, fil):
    """
    Preforms filtering for single filter/file
    """
    with open(os.path.join(folder, filename), 'r') as in_file:
        with open(dest_absolute_path(folder, filename, fil), 'w') as out_file:
            for line in in_file:
                result = fil.filter(line)
                if result:
                    out_file.write(result)


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
            filters = get_filters()
            if filename.endswith(FILE_EXT) and GEN_SUFF not in filename:
                full_name = os.path.join(diag_folder_path, filename)
                mod_time = os.path.getmtime(full_name)
                if full_name not in update_dict or \
                mod_time > update_dict[full_name]:
                    update_dict[full_name] = mod_time
                    for fil in filters:
                        perform_filtering(diag_folder_path, filename, fil)

        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('finished!')

