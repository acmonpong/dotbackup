# dotbackup

A script to backup and restore dotfiles, organized by hostname.

## Usage

The `dotbackup` wrapper script handles virtual environment setup
automatically. Run it from the repository directory:

```sh
./dotbackup
```

### Options

- `-d`, `--dryrun` — Show which files would be copied without actually copying.
- `-v`, `--verbosity` — Set verbosity level (0-4, default 3).

To pass options, run `dotbackup.py` directly within the virtual environment:

```sh
source myenv/bin/activate
python3 dotbackup.py --dryrun
deactivate
```

### Manual virtual environment setup

If you prefer to manage the virtual environment yourself:

```sh
python3 -m venv myenv
source myenv/bin/activate
pip install simple_file_checksum
```

## Configuration

Create a configuration file named \<host\>_dotconf in directory
~/dotfiles. The configuration file consists of two sections "files"
and "destination_dir". Specify what to back up under "files" and
where the files should be backed up under "destination_dir".

Example:

    ## myhost_dotconf

    [files]
    ~/bin/application
    ~/bin/*.sh
    /etc/unbound/unbound.conf

    # Environment variables can be used.
    $HOME/.bash_*

    [destination_dir]
    ~/dotfiles

This configuration will backup the files into the ~/dotfiles
directory.

## Backup structure

The backed up files will be saved into
~/dotfiles/hosts/\<hostname\>/\<path to file\>. For example for a user
named myuser with a configuration file looking like this:

    ## myhost_dotconf

    [files]
    /etc/unbound/unbound.conf
    ~/bin/application

    [destination_dir]
    ~/dotfiles

The backed up file structure in ~/dotfiles would look like this:

    dotfiles
    |-- hosts
        |-- myhost
            |-- etc
            |   |-- unbound
            |       |-- unbound.conf
            |-- home
                |-- myuser
                    |-- bin
                        |-- application
