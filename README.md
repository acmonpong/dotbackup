# dotbackup

A script to backup and restore dotfiles, organized by hostname.

## Usage

The `dotbackup` wrapper script creates the virtual environment
(`myenv`, with the packages from `requirements.txt`) on first run and
passes all its arguments to `dotbackup.py`. It finds the repository
from its own location, so it can be cloned anywhere and symlinked
into your `PATH`:

```sh
ln -s /path/to/dotbackup/dotbackup ~/bin/dotbackup
dotbackup --dryrun
```

On Debian/Ubuntu, creating the virtual environment needs the
`python3-venv` package.

### Options

- `-d`, `--dryrun` — Show which files would be copied without actually copying.
- `-v`, `--verbosity` — Set verbosity level (0-4, default 3).

### Manual virtual environment setup

If you prefer to manage the virtual environment yourself:

```sh
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
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

Symlinks listed in `[files]` (or found while backing up a directory)
are recreated as symlinks in the backup, pointing at the same
target, rather than having their content copied.

The backed up structure is kept in sync with the configuration: if a
file, symlink, or directory is removed from `[files]`, it is deleted
from ~/dotfiles/hosts/\<hostname\> on the next run, along with any
directories left empty as a result.
