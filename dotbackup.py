#!/usr/bin/python3

#
# Copyright (C) 2021 Adrien Martinez
#
# This file is part of dotbackup.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import argparse
import logging
import configparser
import os, sys
import glob
import shutil
from simple_file_checksum import get_checksum

# Instantiate a parser
parser = argparse.ArgumentParser(description="backup dotfiles")

# Add optional argument
parser.add_argument("-v", "--verbosity",
                    type=int,
                    choices=[0, 1, 2, 3, 4],
                    default=3,
                    help="increase output verbosity")
args = parser.parse_args()

if args.verbosity == 4:
    loglevel = "DEBUG"
elif args.verbosity == 3:
    loglevel = "INFO"
elif args.verbosity == 2:
    loglevel = "WARNING"
elif args.verbosity == 1:
    loglevel = "ERROR"
else:
    loglevel = "CRITICAL"

logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=loglevel)

# Instantiate a config parser
config = configparser.ConfigParser(allow_no_value=True)

# Stop parser from turning every filename into lowercase
config.optionxform=str

hostname=os.popen("hostname").read().rstrip()

def get_files(dir_path, level):
    if os.path.isfile(dir_path):
        if level > 4:
            logging.debug("{}|_ {}".format(' ' * level, os.path.basename(dir_path)))
        return [dir_path]

    files_in_dir = []
    for entry in os.scandir(dir_path):
        if entry.is_symlink():
            continue
        if entry.is_dir():
            logging.debug("{}|_ {}".format(' ' * level, entry.name))
            files_in_dir += get_files(entry.path, level + 4)
        else:
            logging.debug("{}|_ {}".format(' ' * level, entry.name))
            files_in_dir += [entry.path]

    return files_in_dir

def files_differs(file1, file2):
    return get_checksum(file1, algorithm="SHA256") == get_checksum(file2, algorithm="SHA256")

def backup_dotfiles(files, destination_root):
    destination = os.path.join(destination_root, 'hosts', hostname)
    logging.debug("Backing up %d files to %s", len(files), destination)

    if not os.path.isdir(destination):
        logging.error("Failed to backup dot files, destination \"%s\" is not a directory", destination)
        return

    i=0
    for f in files:
        i = i + 1
        destination_filepath = os.path.join(os.sep, *destination.split(os.sep), *f.split(os.sep))

	# Check that the file to backup exists
        if not os.path.isfile(f):
            logging.error("Failed to backup dotfile %d, \"%s\" is not a file", i, f)
            exit(1)

	# Check if file has been backed up previously and if they differ
        if os.path.isfile(destination_filepath) and files_differs(destination_filepath, f):
                continue

        try:
            os.makedirs(os.path.dirname(destination_filepath), exist_ok=True)
        except OSError as err:
            logging.error(err)
            return err

        logging.info("{}".format(f))

        try:
            shutil.copyfile(f,destination_filepath)
        except shutil.SameFileError:
            return
        except Exception as e:
            logging.error("Exception: %s, %s", type(e).__name__, e)
            exit(1)

def main():
    files_from_conf = []

    if not hostname:
        logging.error("Hostname is empty")
        exit(1)

    conf_filename = hostname + "_dotconf"
    conf_file_path = os.path.join(os.getenv('HOME'), 'dotfiles/', conf_filename)

    logging.debug("Reading conf file: \"%s\"", conf_file_path)
    if not os.path.exists(conf_file_path):
        logging.error("Configuration file not found")
        exit(1)

    config.read(conf_file_path)

    conf_files = config['files'];
    for f in conf_files:
        expanded_path = os.path.expandvars(os.path.expanduser(f))
        globbed_files = glob.glob(expanded_path)

        if len(globbed_files) == 0:
            if not os.path.isfile(expanded_path) and not os.path.isdir(expanded_path):
                logging.error("%s was expanded to nothing, file/dir do not exists", expanded_path)
                exit(1)

        for gf in globbed_files:
            logging.debug(gf)
            files_from_conf += get_files(gf, 4)

    destinations = config['destination_dir']
    for destination in destinations:
        backup_dotfiles(files_from_conf, os.path.expanduser(destination))

if __name__ == "__main__":
    main()
