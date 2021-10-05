# dotbackup

## Setup
Create a configuration file named <host>_dotconf. The configuration file consists of two sections "files" and "destination_dir". Specify what to be backed up under "files" and where under "destination_dir".

Example:

    [files]
    ~/bin/application
    ~/bin/*.sh
    ~/.bash_*

    [destination_dir]
    ~/dotfiles

This configuration will backup the file ~/bin/application, all files in the bin directory with .sh ending and all files in the homedirectory starting with ".bash_".


