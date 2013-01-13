Spinup
======

Spin up a development VM quickly and easily from the command line. 


This is essentially a wrapper for virtualbox, vagrant, and puppet, but it automates all the setup and makes it possible to spin up a VM for a project with one command.

Installation
------------

To install Spinup, simply download `spinup.py` and store it somewhere -- e.g. in `~/scripts/`. To use it, you can then type in a terminal:

    > python ~/scripts/spinup.py

If you like, you can create a shortcut in your `.bashrc` file, or whatever suits you.

Usage
-----

To use Spinup, you simply need to navigate into the project folder you want a development server for, then run `spinup.py`. 

For instance, suppose I want to build a website in `~/Documents/my-new-website`. I would navigate into that folder, then run `spinup.py`, like this:

    > cd ~/Documents/my-new-website
    > python ~/scripts/spinup.py 

That will start up the interactive Spinup program, which will begin with a screen that looks something like this: 

```

*********************************************

   Welcome to Spinup.
   What would you like to do?

---------------------------------------------

-- `spinup` to spin up your dev box.
-- `exit` to quit
-- `spindown` to shut down your dev box.
-- `help <command>` for help on a specific command
-- `help` for a list of all commands

>> 

```

To spin up a development VM, type: 

    >> spinup 

To boot down your development VM, type: 

    >> spindown

Note: the first time you spin up a VM, it will likely take a long time. This is because it has to download a basic linux box (so be sure you have a good internet connection). After the first time, the VM will boot up much quicker (typically just a couple of minutes). 

The .devbox folder 
------------------

When you run Spinup, it will create a hidden folder called `.devbox` in the current working directory. All special files are contained there. This is much like how git stores its special files in a hidden folder called `.git`. 

Spinup will then create a `Vagrantfile` inside the .devbox folder, and a `manifests` folder. It will also create a basic `default.pp` manifest, which does nothing more than make sure nginx is up and running on your development VM. If you want to modify the manifest, by all means do.

Working on code
---------------

Spinup will mount the current working directory on the VM at `/var/www/root/`. You can configure a webserver on the VM to use that path as its document root. You can then access the webserver on your own computer at 

    http://localhost:8500

or whatever address/port Spinup indicates after it spins up a VM for you. (If 8500 is already taken on your computer, Spinup will try a different port). 

This means you can edit the code in the current working directory just as you normally would, but it will also be available to the VM to use.