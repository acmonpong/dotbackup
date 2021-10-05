# dotbackup

## Setup
Create a configuration file named <host>_dotconf. The configuration file consists of two sections "files" and "destination_dir". Specify what to be backed up under "files" and where under "destination_dir".

Example:

    # myhost_dotconf

    [files]
    ~/bin/application
    ~/bin/*.sh

	# Environment variables can be used.
    $HOME/.bash_*

    [destination_dir]
    ~/dotfiles

This configuration will backup the file ~/bin/application, all files in the bin directory with .sh ending and all files in the home directory starting with ".bash_".


