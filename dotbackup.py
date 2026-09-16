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

parser.add_argument("-d", "--dryrun",
                    action="store_true",
                    help="Do not copy files, only logging")

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

try:
    hostname = os.environ['HOSTNAME']
except KeyError:
    print("The environment variable HOSTNAME is not set.")
    exit(1)

def get_files(dir_path):
    # dir_path is a leaf: a plain file, or a symlink (to a file or a
    # directory). Symlinks are returned as-is, never followed, so they
    # can be recreated as symlinks in the backup instead of being
    # walked into or dereferenced.
    if os.path.islink(dir_path) or os.path.isfile(dir_path):
        return [dir_path]

    # dir_path is a real directory: recurse into each entry. The leaf
    # check above handles files and symlinks, so only real
    # subdirectories actually recurse further.
    files_in_dir = []
    for entry in os.scandir(dir_path):
        logging.debug(entry.path)
        files_in_dir += get_files(entry.path)

    return files_in_dir

def files_equal(file1, file2):
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        return False
    return get_checksum(file1, algorithm="SHA256") == get_checksum(file2, algorithm="SHA256")

def update_symlink(src, dst):
    # Read the target string the source symlink points to, e.g.
    # "real.txt" or "../dotfiles/vimrc". This is copied as-is, never
    # resolved/followed.
    target = os.readlink(src)

    # Already backed up: dst is a symlink pointing at the same target.
    if os.path.islink(dst) and os.readlink(dst) == target:
        return

    print("{}".format(src))

    if args.dryrun:
        return

    # Make sure the destination is within a directory that exists
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    except OSError as err:
        logging.error(err)
        return err

    # os.symlink() fails if dst already exists, so remove whatever is
    # there first (a stale symlink, or a leftover regular file).
    # lexists (not exists) is used so a broken symlink at dst is still
    # detected and removed, instead of being missed because its
    # target no longer exists.
    if os.path.lexists(dst):
        os.remove(dst)

    # Recreate the symlink at dst with the same target string as src.
    try:
        os.symlink(target, dst)
    except Exception as e:
        logging.error("Exception: %s, %s", type(e).__name__, e)
        exit(1)

def update_file(src, dst):
    if os.path.islink(src):
        update_symlink(src, dst)
        return

    # Check that the file exists
    if not os.path.isfile(src):
        logging.warning("Failed to update, %s is not a file", src)
        return

    # Check if files differ
    if files_equal(src, dst):
        return

    print("{}".format(src))

    if args.dryrun:
        return

    # Make sure the destination is within a directory that exists
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    except OSError as err:
        logging.error(err)
        return err

    try:
        shutil.copyfile(src, dst)
    except shutil.SameFileError:
        return
    except Exception as e:
        logging.error("Exception: %s, %s", type(e).__name__, e)
        exit(1)

def backup_dotfiles(files, dotfiles_root_dir):
    dotfiles_host_dir = os.path.join(dotfiles_root_dir, 'hosts', hostname)
    for f in files:
        # f is an absolute path; strip its leading separator so
        # os.path.join appends it under dotfiles_host_dir instead of
        # treating it as an absolute path on its own.
        dotfile = os.path.join(dotfiles_host_dir, f.lstrip(os.sep))
        update_file(f, dotfile)


def load_config(hostname):
    conf_filename = hostname + "_dotconf"
    conf_file_path = os.path.join(os.getenv('HOME'), 'dotfiles/', conf_filename)

    logging.debug("Reading conf file: \"%s\"", conf_file_path)
    if not os.path.exists(conf_file_path):
        logging.error("Configuration file not found")
        exit(1)

    # Instantiate a config parser
    config = configparser.ConfigParser(allow_no_value=True)

    # Stop parser from turning every filename into lowercase
    config.optionxform = str

    config.read(conf_file_path)
    return config

def validate_config(config):
    if not config.has_section("files"):
        logging.error("Configuration has no files section")
        exit(1)

    if not config.has_section("destination_dir"):
        logging.error("Configuration has no destination_dir section")
        exit(1)

    if len(config["destination_dir"]) == 0:
        logging.error("Configuration needs at least one destination")
        exit(1)

def expand_conf_files(conf_files):
    files_from_conf = []
    for f in conf_files:
        expanded_path = os.path.expandvars(os.path.expanduser(f))
        globbed_files = glob.glob(expanded_path)

        if len(globbed_files) == 0:
            logging.error("%s was expanded to nothing, file/dir do not exists", expanded_path)
            exit(1)

        for gf in globbed_files:
            logging.debug(gf)
            files_from_conf += get_files(gf)

    return files_from_conf

def main():
    if not hostname:
        logging.error("Hostname is empty")
        exit(1)

    config = load_config(hostname)
    validate_config(config)

    files_from_conf = expand_conf_files(config['files'])

    for destination in config['destination_dir']:
        backup_dotfiles(files_from_conf, os.path.expanduser(destination))

if __name__ == "__main__":
    main()
