Spinup
======

Spin up a development VM quickly and easily from the command line. This is essentially a wrapper for virtualbox, vagrant, and puppet, but it automates all the setup and makes it possible to spin up a VM for a project with one command.

Usage
-----

To use spinup, navigate to the project folder you want a development server for, then run spinup.py. 

That will start the interactive Spinup program, which will look something like this: 

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

    spinup 

To boot down your development VM, type: 

    spindown

Note: the first time you spin up a VM, it will likely take a long time. This is because it has to download a basic linux box (so be sure you have a good internet connection). After the first time, the VM will boot up much quicker (typically just a couple of minutes). 

The .devbox folder 
------------------

When you run Spinup, it will create a hidden folder called `.devbox` in the current working directory. All special files are contained there. This is much like how git stores its special files in a hidden folder called `.git`. 

Spinup will then create a `Vagrantfile` inside the .devbox folder, as well as a `manifests` folder. If you want to include a puppet manifest, add it as `default.pp` inside the `manifests` folder.

