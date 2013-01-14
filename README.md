Spinup
======

Spin up a development VM quickly and easily from the command line. 


This is essentially a wrapper for virtualbox, vagrant, and puppet, but it automates all the setup and makes it possible to spin up a VM for a project with one command.

Requirements
------------

I have only tried Spinup on my own machine, so I cannot say that it will work on other machines. But it is currently meant to work on Ubuntu based Linux OSes.

I hope to get it working on OS X at some point in the near future, and Windows too (eventually). At the moment, this is still just a prototype, meant mainly for easing my own development cycle.

(The reason Spinup only works on Ubuntu OSes is because it relies on `apt-get` to install VirtualBox, Vagrant, and Puppet, if they're not already installed. In theory, Spinup should also work on the RedHat family of OSes, using `yum` instead of `apt-get`, but I haven't tried it. I wager it still needs some tweaking to work properly on those systems.)


Installation
------------

To install Spinup, simply download `spinup.py` and store it somewhere -- e.g. in `~/scripts/`. To use it, you can then type in a terminal:

    > python ~/scripts/spinup.py

If you like, you can create a shortcut in your `.bashrc` file, or whatever suits you.

Usage
-----

To use Spinup, navigate into the project folder you want a development server for, then run `spinup.py`. 

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

(Note: the first time you do this, it will likely take a long time. This is because Spinup has to download a basic linux box (so be sure you have a good internet connection). After the first time though, it is much quicker.)

When the development box starts booting up, you will see a lot of output getting spit out on the command line, but when all is said and done, Spinup will tell you that your development box is ready. The screen will look something like this: 

```
*********************************************


   READY
   -----------------------------------

   The dev box is ready for use.
   You can reach your site at this address:

   -- http://localhost:8500


-- `spindown` to shut down your dev box.
-- `help` for a list of all commands
-- `exit` to quit
-- `ssh` to ssh into your dev box.
-- `help <command>` for help on a specific command

>> 
```

If you then point your browser to `http://localhost:8500` (or whatever url Spinup gives you), you'll see a working web page. If you look in your current working directory, you'll see an `index.html` file. That's the file you see at `http://localhost:8500`. The VM's webserver (nginx) is now pointing at your current working directory, so you can build a website there.

You can exit the Spinup program and come back to it as many times as you like, but the VM will stay running in the background, even when Spinup is not running.

If you want to boot down your development box, type: 

    >> spindown

You can boot up your dev box again by navigating into the project folder and running `spinup.py` again.

The .devbox folder 
------------------

When you run Spinup, it will create a hidden folder called `.devbox` in the current working directory. All special files are contained there. This is much like how git stores its special files in a hidden folder called `.git`. 

Spinup will then create a `Vagrantfile` inside the `.devbox` folder, and the `Vagrantfile` is the configuration file for vagrant. You can edit it as you see fit; Spinup will only modify forwarded ports if there are port conflicts that it needs to resolve.

Spinup will also create in `.devbox` a `manifests` folder and a basic `default.pp` file. The `default.pp` manifest does little more than make sure nginx is up and running on your development VM, and that it points to your current working directory. If you want to modify the manifest file, by all means do. Spinup will not overwrite your changes. 

