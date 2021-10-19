# dotbackup

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



    