# dotbackup

## Python virtual environment setup
Setup the virtual environment by running this in the same folder as dotbackup.py.

python -m venv myenv

To activate the virtual environment, run:

source myenv/bin/activate

After activation it is possible to install all needed dependencies. If
pip is missing, start by running:

python3 -m ensurepip --default-pip

After that, install modules by running:

python3 -m pip install <module name>

## Running the script within the virtual environment
From the same directory as dotbackup.py, activate the environment:

source myenv/bin/activate
python3 dotbackup.py
deactivate

A sample script is name dotbackup in the repository.

## Setup
Create a configuration file named \<host\>_dotconf in directory
~/dotfiles. The configuration file consists of two sections "files"
and "destination_dir". Specify what to be backed up under "files" and
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




