#! /usr/bin/env python3

# CAmera Trap Image Renamer (CATIR) for the
# Urban Fishing Cat Conservation Project (fishingcats.lk)
# Author: Mahangu Weerasinghe (mahangu@gmail.com)
# This is a project-specific fork, and is not intended for 
# mass release or distribution. 
#
# Forked from:
# smart-image-renamer
# Author: Ronak Gandhi (ronak.gandhi@ronakg.com)
# Project Home Page: https://github.com/ronakg/smart-image-renamer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Smart Image Renamer main module"""

import argparse
import itertools
import os
import re
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS

# Hideous monkeypatch. ymmv
from PIL import JpegImagePlugin

JpegImagePlugin._getmp = lambda x: None


class NotAnImageFile(Exception):
    """This file is not an Image"""
    pass


class InvalidExifData(Exception):
    """Could not find any EXIF or corrupted EXIF"""
    pass


def get_argparse_epilog():
    usage = "Possible arguments:\n"
    parser = argparse.ArgumentParser(add_help=False)
    for action in parser._actions:
        if action.option_strings:
            usage += ', '.join(action.option_strings)
            usage += f": {action.help}\n"
    return usage


def get_cmd_args():
    """Get, process and return command line arguments to the script
    """
    help_description = '''
CAmera Trap Image Renamer (CATIR)
Urban Fishing Cat Conservation Project (fishingcats.lk)
https://github.com/mahangu/catir/

Rename camera trap images according to a set format, incrementing seconds if
duplicates are found.

Forked from: https://github.com/ronakg/smart-image-renamer
'''

    parser = argparse.ArgumentParser(description=help_description,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=get_argparse_epilog())

    parser.add_argument('-s', dest='sequence', type=int, default=1,
                        help='Starting sequence number (default: 1)')
    parser.add_argument('-r', dest='recursive', default=False,
                        action='store_true',
                        help='Recursive mode')
    parser.add_argument('-i', dest='hidden', default=False,
                        action='store_true', help='Include hidden files')
    parser.add_argument('-t', dest='test', default=False, action='store_true',
                        help='Test mode. Don\'t apply changes.')
    parser.add_argument('--deployment-name', dest='deployment_name', default=None,
                        help='Deployment name (default: derived from directory structure)')
    parser.add_argument('--timestamp-format', dest='timestamp_format', default='{YYYY}-{MM}-{DD}_{hh}-{mm}-{ss}',
                        help='Custom input format for filename (default: "{YYYY}-{MM}-{DD}_{hh}-{mm}-{ss}")')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('input', nargs='+',
                        help='Absolute path to file or directory')

    return parser.parse_args()


def get_exif_data(img_file):
    """Read EXIF data from the image.

    img_file: Absolute path to the image file

    Returns: A dictionary containing EXIF data of the file

    Raises: NotAnImageFile if file is not an image
            InvalidExifData if EXIF can't be processed
    """
    try:
        img = Image.open(img_file)
    except (OSError, IOError):
        raise NotAnImageFile

    try:
        # Use TAGS module to make EXIF data human readable
        exif_data = {
            TAGS[k]: v
            for k, v in img._getexif().items()
            if k in TAGS
        }
    except AttributeError:
        raise InvalidExifData

    # Add image format to EXIF
    exif_data['format'] = img.format
    return exif_data


def main():
    """Read CLI arguments and execute the script"""

    skipped_files = []
    args = get_cmd_args()

    input_paths = [os.path.abspath(input) for input in args.input]
    timestamp_format = args.timestamp_format
    verbose = args.verbose
    quiet = args.quiet
    sequence_start = args.sequence
    test_mode = args.test
    recursive = args.recursive
    include_hidden = args.hidden
    deployment_name = args.deployment_name

    for input_path in input_paths:
        for root, dirs, files in os.walk(input_path):
            # Skip hidden directories unless specified by user 
            if not include_hidden and os.path.basename(root).startswith('.'):
                continue

            # Initialize sequence counter
            # Use no of files to determine padding for sequence numbers
            seq = itertools.count(start=sequence_start)
            seq_width = len(str(len(files)))

            print('Processing folder: {}'.format(root))

            unduplicator = 1

            for f in sorted(files):
                # Skip hidden files unless specified by user 
                if not include_hidden and f.startswith('.'):
                    continue

                old_file_name = os.path.join(root, f)
                try:
                    # Get EXIF data from the image
                    exif_data = get_exif_data(old_file_name)
                except NotAnImageFile:
                    continue
                except InvalidExifData:
                    skipped_files.append((old_file_name, 'No EXIF data found'))
                    continue

                # Find out the original timestamp or digitized timestamp from the EXIF
                img_timestamp = (exif_data.get('DateTimeOriginal') or
                                 exif_data.get('DateTimeDigitized'))

                if not img_timestamp:
                    skipped_files.append((old_file_name,
                                          'No timestamp found in image EXIF'))
                    continue

                # Extract year, month, day, hours, minutes, seconds from timestamp
                img_timestamp = \
                    re.search(r'(?P<YYYY>\d\d\d?\d?):(?P<MM>\d\d?):(?P<DD>\d\d?) '
                              '(?P<hh>\d\d?):(?P<mm>\d\d?):(?P<ss>\d\d?)',
                              img_timestamp.strip())

                if not img_timestamp:
                    skipped_files.append((old_file_name,
                                          'Timestamp not in correct format'))
                    continue

                # Generate data to be replaced in user provided format
                new_image_data = {'Artist': exif_data.get('Artist', ''),
                                  'Make': exif_data.get('Make', ''),
                                  'Model': exif_data.get('Model', ''),
                                  'Folder': os.path.basename(root),
                                  'Seq': '{0:0{1}d}'.format(next(seq), seq_width),
                                  'ext': exif_data.get('format', '')
                                  }
                new_image_data.update(img_timestamp.groupdict())

                # Generate new file name according to user provided format
                new_file_name = (timestamp_format + '.{ext}').format(**new_image_data)
                new_file_name_with_path = os.path.join(root, new_file_name)
                import os.path as path

                if not deployment_name:
                    deployment_name = new_file_name_with_path.split("/")[-5]
                new_file_name_complete = os.path.join(root, deployment_name + "_" + new_file_name)

                # Don't overwrite an already existing file. Instead, increment {ss} until we have a unique filename.
                while (os.path.isfile(new_file_name_complete)):
                    print("Duplicate file found: " + new_file_name_complete)

                    current_args = new_file_name.split('.', 1)
                    seconds = int(current_args[0][-2:])
                    rest_of_args = current_args[0][:17]
                    seconds += 1

                    new_file_name = (rest_of_args + str(seconds).zfill(2) + '.{ext}').format(**new_image_data)
                    new_file_name_complete = os.path.join(root, deployment_name + "_" + new_file_name)

                    print("Renaming file to: " + new_file_name_complete)

                # Don't rename files if we are running in test mode
                if not test_mode:
                    try:
                        os.rename(old_file_name, new_file_name_complete)
                    except OSError:
                        skipped_files.append((old_file_name,
                                              'Failed to rename file'))
                        continue

                if verbose:
                    print('{0} --> {1}'.format(old_file_name,
                                               new_file_name_complete))
                elif not quiet:
                    print('{0} --> {1}'.format(f, new_file_name))

            # Folder processed
            print('')

            # Break if recursive flag is not present
            if not recursive:
                break

    # Print skipped files
    if skipped_files and not quiet:
        print('\nSkipped Files:\n\t' + '\n\t'.join([file + ' (' + error + ')'
                                                    for file, error in
                                                    skipped_files]))


if __name__ == '__main__':
    main()
