"""


SPIN UP - Get a virtual development environment 
running on your computer.

This script installs virtualbox, vagrant, and puppet 
on your computer, then it sets up a virtual box
 that you can use as your development server.

It currently only supports OSes in the Ubuntu Linux 
family. Perhaps someday it will be expanded to handle 
OSes in the Redhat family, OS X, and Windows too.

"""

#########################################################
#########################################################
# A utilities class:

class Utilities:
    """
    A class that has a number of helper methods.
    """

    @staticmethod
    def show_error(message):
        """
        For prettier error messages. This function
        splits up a message into lines with 6 words
        each, then prints it out in a nicer format.
        """
        words = message.split()
        line_length = 6
        formatted_message = ''
        for word in range(0, len(words), line_length):
            words_for_line = words[word:word+line_length]
            formatted_message += '\n\r  |  ' + ' '.join(words_for_line)
        print ' '
        print '  ----------------------------------------'
        print '  |'
        print '  |  Oops! '
        print '  ----------------------------------------'
        print '  | ' + formatted_message
        print '  |'
        print '  ----------------------------------------'
        print ' '
        exit()


    @staticmethod
    def import_or_catch(package):
        """ 
        Try to import a package, but catch the error 
        if it fails and show a pretty message.
        """
        try:
            module = __import__(package)
        except:
            message = """
                I couldn't import the \"""" + package + """\" package.
                Make sure it's installed and in your python path.
            """
            Utilities.show_error(message)
        else:
            return module


    @staticmethod
    def file_exists(file):
        """ 
        Make sure a file exists. 
        """
        try:
            with open(file): return True
        except IOError:
            return False


    @staticmethod
    def create_folder(folder):
        """
        Attempts to create a folder in the current directory.
        Returns a tuple:
        -- (True, exception) if the folder exists already.
        -- (False, 'permissions') if access was denied.
        -- (False, exception) for all other errors.
        """
        try:
            os.mkdir(folder, 0740)
        except OSError as exception:
            if exception.errno == errno.EEXIST:
                return (True, exception)
            elif exception.errno == errno.EACCES:
                return (False, 'permissions')
            else:
                return (False, exception)
        else:
            return (True, None)


    @staticmethod
    def write_file(path, contents):
        """
        Attempts to write a file to disk.
        Returns a tuple:
        -- (True, path) if successful.
        -- (False, 'permissions') if access was denied.
        -- (False, exception) for all other errors.
        """
        try:
            file = open(path, 'w+')
        except IOError as exception:
            if exception.errno == errno.EACCES:
                return (False, 'permissions')
            else:
                return (False, exception)
        else:
            file.write(contents)
            file.close()
            return (True, path)



#########################################################
#########################################################
# Import the modules we need

subprocess = Utilities.import_or_catch('subprocess')
errno = Utilities.import_or_catch('errno')
cmd = Utilities.import_or_catch('cmd')
platform = Utilities.import_or_catch('platform')
sys = Utilities.import_or_catch('sys')
os = Utilities.import_or_catch('os')
fileinput = Utilities.import_or_catch('fileinput')



#########################################################
#########################################################
# A dictionary for data

class Data:
    """
    A dictionary to store data in.
    """
    vagrant_folder = '.devbox'
    vagrant_file = vagrant_folder + os.sep + 'Vagrantfile'
    manifests_folder = vagrant_folder + os.sep + 'manifests'
    manifests_file = manifests_folder + os.sep + 'default.pp'
    port = 8500
    box = 'lucid64'
    box_url = 'http://files.vagrantup.com/lucid64.box'
    code_folder_name = 'root'
    code_folder_path_on_box = '/var/www/' + code_folder_name



#########################################################
#########################################################
# An installer class

class Installer:
    """
    This class tries to install the following 
    required software:
    -- Virtual Box
    -- Vagrant
    -- Puppet
    """

    # The required software that needs to be installed.
    required_software = ['virtualbox', 'vagrant', 'puppet']

    # Linux package managers/installers.
    linux_installers = ['apt-get', 'yum']


    def __init__(self, data):
        """
        Initializes the installer by storing some data.
        """
        self.data = data


    def program_exists_on_nix(self, program):
        """
        Checks if a program exists on a *nix system.
        Returns the path to the program if it exists,
        False otherwise.
        """
        try:
            return subprocess.check_output(['which', program])
        except subprocess.CalledProcessError:
            return False


    def find_linux_package_manager(self):
        """
        Tries to identify the Linux package manager (apt-get, yum, etc.).
        """

        # See if any package manager/installers exist on the system.
        installer = None
        for program in self.linux_installers:
            package_manager = self.program_exists_on_nix(program)
            if package_manager is not False:
                installer = package_manager.strip()

        # If no package manager was found, report an error. To report
        # an error in proper English, we need to format strings that
        # make grammatical sense when speaking about one item, two items,
        # or a whole list of items. That's what all the `if` statements 
        # you'll see below are about.
        if installer is None:
            length = len(self.linux_installers)
            installers = ''
            if length == 1:
                installers = self.linux_installers[0]
            elif length == 2:
                installers += self.linux_installers[0]
                installers += ' and '
                installers += self.linux_installers[1]
            elif length > 2:
                for installer in self.linux_installers[:-1]:
                    installers += installer + ', ' 
                installers += ' and '
                installers += self.linux_installers[length - 1]
            if length == 1:
                pluralized = 'which does not'
            elif length == 2:
                pluralized = 'neither of which'
            elif length > 2:
                pluralized = 'none of which'
            message = """
                I cannot find your package manager. 
                I looked for """ + installers + """,
                """ + pluralized + """ appear to be 
                on your system. I'm sorry, but I cannot 
                install the programs I need to spin up a
                development environment. You could try 
                installing the required software manually 
                and then starting me up again.
            """
            Utilities.show_error(message)

        # Otherwise, we found a package manager/installer, so we can
        # simply return it. This will be, e.g. '/usr/bin/apt-get'
        else:
            return installer


    def install_program_on_linux(self, program):
        """
        Try to install a program on linux with whichever
        package manager we've found on the system.
        """

        # Show a message
        print "-- Attempting to install " + program + "..."

        # Run the `install` command
        cmd = ['sudo', self.data.package_manager, '-y', 'install', program]
        try:
            result = subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            message = """
                Unfortunately, I was not able to install """ + program + """.
                You could try to install it yourself, then run me again.
                If I can find it next time, I won't hassle you anymore 
                about it. 
            """
            Utilities.show_error(message)
        else:

            # Report that all is done.
            print '---- Done.'


    def install_linux_software(self):
        """
        Installs the requisite software for Linux.
        """
 
        # Get the package manager/installer.
        self.data.package_manager = self.find_linux_package_manager()

        # Install each program.
        for program in self.required_software:
            if not self.program_exists_on_nix(program):
                self.install_program_on_linux(program)

        # Add vagrant to PATH (this only needs to be done on Linux)
        path = os.environ["PATH"]
        if '/opt/vagrant/bin' not in path:
            os.environ["PATH"] = path + ':/opt/vagrant/bin'

        # Report that all is good (errors would have been raised 
        # already if something went wrong). 
        print ""
        print "Good! I've installed all the required software."
        return True


    def setup(self):
        """
        Set up the required software on the system.
        """

        # If this is linux...
        if self.data.os == 'linux':

            # Only proceed if the requisite programs are not installed.
            ready = True
            for program in self.required_software:
                if not self.program_exists_on_nix(program):
                    ready = False

            if not ready:

                # Give a message about what's up
                print "-------------------------------"
                print "I need to install some programs."

                # Install the software
                return self.install_linux_software()

            # The requisite programs are already installed.
            else:
                return True 



#########################################################
#########################################################
# A class that sets up puppet provisioning

class Provisioner:
    """
    The `Provisioner` class creates puppet manifest
    files for provisioning dev boxes.
    """

    def __init__(self, data):
        """ 
        Initializes the provisioner by storing some data.
        """
        self.data = data


    def basic_nginx(self):
        """
        Returns a basic nginx manifest that points to 
        the current cwd as the web root.
        """

        # Check if there is an index.html file in the cwd already.
        # If not, we'll create one
        cwd = str(os.path.realpath(os.getcwd()))
        filename = cwd + os.sep + 'index.html'
        index_file = Utilities.file_exists(filename)

        # Construct a basic manifest that makes sure nginx
        # is up and running and points to the cwd as its web root.
        nginx = '# Make sure Nginx is installed.\n'
        nginx += "package { 'nginx':\n"
        nginx += '    ensure => present,\n'
        nginx += '}\n'
        nginx += '\n'
        nginx += '# Rewrite the virtual hosts file\n'
        nginx += "file { '/etc/nginx/sites-available/default':\n"
        nginx += "    require => Package['nginx'],\n"
        nginx += "    content => '\n"
        nginx += "server {\n"
        nginx += '    listen      80;\n'
        nginx += '    server_name localhost;\n'
        nginx += '\n'
        nginx += '    index       index.html;\n'
        nginx += '    root        ' + self.data.code_folder_path_on_box + ';\n'
        nginx += "}',\n"
        nginx += '}\n'
        nginx += '\n'
        if not index_file:
            nginx += '# Create an index file\n'
            nginx += "file { '" + self.data.code_folder_path_on_box 
            nginx +=          "/index.html':\n"
            nginx += "    require => File["
            nginx +=      "'/etc/nginx/sites-available/default'],\n"
            nginx += "    content => '\n"
            nginx += '<html><h1>Welcome to your nginx site.</h1></html>\n'
            nginx += "',\n"
            nginx += '}\n'
            nginx += '\n'
        nginx += '# Make sure nginx is running.\n'
        nginx += "service { 'nginx':\n"
        nginx += '    ensure => running,\n'
        nginx += "    require => File[" 
        if not index_file:
            nginx +=  "'" + self.data.code_folder_path_on_box 
            nginx +=  "/index.html'],\n"
        else: 
            nginx +=  "'/etc/nginx/sites-available/default'],\n"
        nginx += '}\n'
        nginx += '\n'

        return nginx


    def manifest(self):
        """
        Creates a puppet manifest file.
        """

        # If no puppet manifest exists, try and create one.
        if not Utilities.file_exists(self.data.manifests_file):

            # Try to write the file
            contents = self.basic_nginx()
            result = Utilities.write_file(self.data.manifests_file, contents)

            # Handle errors
            if result[0] is False:
                if result[1] is 'permissions':
                    message = """
                        I could not create a puppet manifest file
                        in `""" + self.data.manifest_folder + """`, 
                        because I don't have permission. Change the 
                        permissions to something like 740, then 
                        run me again.
                    """
                else:
                    message = """
                        I'm sorry, but I could not create a puppet 
                        manifest file. The error message I received
                        was this: """ + str(result[1]) + """.
                    """
                Utilities.show_error(message)



#########################################################
#########################################################
# A class that sets up a vagrant/puppet environment

class Setup:
    """
    The `Setup` class is responsible for setting up
    the vagrant/puppet environment. This involves:
    (a) creating a `.devbox` folder in the cwd,
    (b) creating a `Vagrantfile` in `.devbox`, and
    (c) creating a `manifests` folder in `.devbox`,
        using the Provisioner class.
    """

    def __init__(self, data):
        """
        Initializes the setup by storing some data.
        """
        self.data = data


    def setup_box(self):
        """
        Sets up a development box.
        """

        # Try to create a folder to house the vagrant VM
        # (if the folder does not already exist)
        devbox_result = Utilities.create_folder(self.data.vagrant_folder)

        # Handle errors.
        if devbox_result[0] is False:
            if devbox_result[1] is 'permissions':
                message = """
                    I could not create a 
                    `""" + self.data.vagrant_folder + """` folder
                    to house the development box, because I
                    do not have permission to do so. Try 
                    changing the permissions so I can create
                    a folder in this directory, then run me again.
                """
            else:
               message = """
                   I could not create a 
                   `""" + self.data.vagrant_folder + """` folder
                   to house the development box. The error 
                   message I received was this: 
                   """ + str(devbox_result[1]) + """.
               """
            Utilities.show_error(message) 

        # Try to create the puppet manifest folder 
        # (if it does not already exist)
        manifests_result = Utilities.create_folder(self.data.manifests_folder)

        # Handle errors
        if manifests_result[0] is False:
            if manifests_result[1] is 'permissions':
                message = """
                    I could not create a `manifests` folder
                    in the `""" + self.data.vagrant_folder + """` 
                    directory, because I do not have the permission. 
                    Try changing the permissions so I can create
                    a folder in that directory, then run me again.
                """
            else:
               message = """
                   I could not create a `manifests` folder
                   in the `""" + self.data.vagrant_folder + """` 
                   directory. The error message I received was this: 
                   """ + str(manifests_result[1]) + """.
               """
            Utilities.show_error(message)

        # Initialize a puppet manifest.
        self.data.provisioner.manifest()

        # Initialize vagrant.
        self.initialize_vagrant()


    def initialize_vagrant(self):
        """
        Initializes vagrant by modifying or creating a 
        custom `Vagrantfile`. If the file exists already,
        this method can still overwrite the specified port,
        the box name, and the box url.
        """

        # Establish some useful values.
        box = str(self.data.box)
        box_url = str(self.data.box_url)
        port = str(self.data.port)
        code_folder_name = str(self.data.code_folder_name)
        code_folder_path_on_box = str(self.data.code_folder_path_on_box)
        code_folder_path_on_host = str(os.path.realpath(os.getcwd()))

        # Check if a puppet manifest exists
        manifests = Utilities.file_exists(self.data.manifests_file)

        # We'll build the vagrant file in this string.
        contents = ''

        # If the Vagrantfile exists, read it line by line 
        # and replace any bits that matter.
        if Utilities.file_exists(self.data.vagrant_file):
            for line in fileinput.input([self.data.vagrant_file]):

                # Modify the box name line if a new name was specified
                if 'config.vm.box = ' in line:
                    if hasattr(self.data, 'new_box'):
                        contents += '  config.vm.box = "'
                        contents += str(self.data.new_box) + '"\n'
                    else:
                        contents += line

                # Modify the box url line if a new box url was specified
                elif 'config.vm.box_url = ' in line:
                    if hasattr(self.data, 'new_box_url'):
                        contents += '  config.vm.box_url = "'
                        contents += str(self.data.new_box_url) + '"\n'
                    else:
                        contents += line

                # Modify the port line if a new port was specified
                elif 'config.vm.forward_port 80,' in line:
                    if hasattr(self.data, 'new_port'):
                        contents += '  config.vm.forward_port 80, '
                        contents += str(self.data.new_port) + '\n'
                        self.data.port = self.data.new_port
                    else:
                        contents += line
                        parts = line.split('config.vm.forward_port 80,')
                        new_port = parts[1].strip()
                        self.data.port = new_port

                # Otherwise, leave the line as it is.
                else:
                    contents += line

        # Otherwise, we need to construct the file from scratch
        else:
            contents += '# -*- mode: ruby -*-' + "\n"
            contents += '# vi: set ft=ruby :' + "\n"
            contents += "\n"
            contents += 'Vagrant::Config.run do |config|' + "\n"
            contents += "\n"
            contents += "  # The base box to build off of.\n"
            contents += '  config.vm.box = "' + box + '"' + "\n"
            contents += "\n"
            contents += "  # The url to download the box from.\n"
            contents += '  config.vm.box_url = "' + box_url + '"' + "\n"
            contents += "\n"
            contents += "  # Bridge the box's network to your computer's.\n"
            contents += '  config.vm.network :bridged' + "\n"
            contents += "\n"
            contents += "  # Hook the box's ports up to your computer's.\n"
            contents += '  config.vm.forward_port 80, ' 
            contents +=    port + "\n"
            contents += "\n"
            contents += "  # Share a folder with the box.\n"
            contents += '  config.vm.share_folder "' 
            contents +=    code_folder_name + '", '
            contents +=    '"' + code_folder_path_on_box + '", '
            contents +=    '"' + code_folder_path_on_host + '", '
            contents +=    ':create => true' + "\n" 
            contents += "\n"
            contents += "  # Allow symlinks in the shared folder.\n"
            contents += '  config.vm.customize ["setextradata", :id, '
            contents +=    '"VBoxInternal2/SharedFoldersEnableSymlinksCreate/'
            contents +=    code_folder_name + '", "1"]'
            contents += "\n"
            contents += "  # Let Puppet do the provisioning.\n"
            contents += '  config.vm.provision :puppet, '
            contents +=    ':options => \'--verbose\'' + "\n"
            contents += "\n"
            contents += 'end' + "\n"

        # Write the file
        result = Utilities.write_file(self.data.vagrant_file, contents)

        # Handle errors
        if result[0] is False:
            if result[1] is 'permissions':
                message = """
                    I could not create the Vagrant configuration
                    file in `""" + self.data.vagrant_folder + """`, 
                    because I don't have permission. Change the 
                    permissions to something like 740, then 
                    run me again.
                """
            else:
                message = """
                    I'm sorry, but I could not create the Vagrant 
                    configuration file. The error message I received
                    was this: """ + str(result[1]) + """.
                """
            Utilities.show_error(message)



#########################################################
#########################################################
# A class that creates/boots dev boxes

class Spinner:
    """ 
    The `Spinner` class is responsible for spinning up 
    and spinning down development boxes.
    """

    def __init__(self, data):
        """
        Initializes the spinner by storing some data.
        """
        self.data = data


    def cd_into_vagrant(self):
        """
        Change directories into the vagrant folder 
        """

        # Exit if we're in the vagrant folder already
        cwd = os.path.realpath(os.getcwd())
        path_parts = cwd.split(os.sep)
        current_folder = path_parts[-1]
        if current_folder == self.data.vagrant_folder:
            return

        # Try and cd into the vagrant folder.
        else:
            try:
                os.chdir(self.data.vagrant_folder)
            except OSError:
                message = """
                    I was not able to get into the 
                    `""" + self.data.vagrant_folder + """` 
                    folder in this directory.
                    Try checking the permissions, then 
                    run me again.
                """
                Utilities.show_error(message)


    def cd_out_of_vagrant(self):
        """
        Change directories out of the vagrant folder 
        """

        # Exit if we're not in the vagrant folder
        cwd = os.path.realpath(os.getcwd())
        path_parts = cwd.split(os.sep)
        current_folder = path_parts[-1]
        if current_folder != self.data.vagrant_folder:
            return

        # Try and cd out of the vagrant folder.
        else:
            try:
                os.chdir('..')
            except OSError:
                message = """
                    I was not able to get out of the 
                    `""" + self.data.vagrant_folder + """` 
                    folder in this directory.
                    Try checking the permissions, then 
                    run me again.
                """
                Utilities.show_error(message)


    def shut_down_box(self):
        """
        Shut down a development box with `vagrant halt`
        """

        # Change into the vagrant folder
        self.cd_into_vagrant()

        # Try to boot down the vagrant box
        try:
            result = subprocess.check_call(['vagrant', 'halt'])
        except subprocess.CalledProcessError as exception:
            message = """
                I could not shut down your dev box. 
                The error message I received was this: 
                """ + str(exception) + """.
            """
            Utilities.show_error(message) 
        else:
            message =  "\n"
            message += "\n"
            message += "*********************************************\n\n"
            message += "\n"
            message += "   The dev box successfully shut down.\n"
            message += "\n"
            print message

        # Get out of the vagrant folder
        self.cd_out_of_vagrant()


    def boot_up_box(self):
        """
        Boot up a development box with `vagrant up`
        """

        # Change into the vagrant folder
        self.cd_into_vagrant() 

        # Try to boot up the vagrant box
        try: 
            result = subprocess.check_call(['vagrant', 'up'])
        except subprocess.CalledProcessError as exception:
            if exception.returncode is 26:
                self.data.new_port = self.data.port + 1
                message = """
                    The port """ + str(self.data.port) + """
                    is already in use. Trying again with 
                    port """ + str(self.data.new_port) + """.
                """
                print message
                self.shut_down_box()
                self.spinup()
            else:
                message = """
                    I could not boot up the development box. 
                    You could try navigating into the 
                    `""" + self.data.vagrant_folder + """`
                    folder and running the `vagrant up` command.
                """
                Utilities.show_error(message)
        else:
            message =  "\n"
            message += "\n"
            message += "*********************************************\n\n"
            message += "\n"
            message += '   READY' + "\n"
            message += "   -----------------------------------\n"
            message += "\n"
            message += "   The dev box is ready for use.\n"
            message += "   You can reach your site at this address:\n"
            message += "\n"
            message += '   -- http://localhost:' + str(self.data.port) + "\n"
            message += "\n"
            print message

        # Get out of the vagrant folder
        self.cd_out_of_vagrant()


    def spinup(self, arguments={}):
        """
        Spins up a development box.
        """

        # Store the box (if a box is specified)
        if 'box' in arguments:
            self.data.new_box = arguments['box']

        # Store the box url (if one is specified)
        if 'box-url' in arguments:
            self.data.new_box_url = arguments['box-url']

        # Store the port (if a port is specified)
        if 'port' in arguments:
            self.data.new_port = arguments['port']

        # Setup the box
        self.data.setup.setup_box()

        # Boot up the machine
        self.boot_up_box()


    def spindown(self):
        """
        Spins down the development box.
        """
        self.shut_down_box()


    def ssh(self):
        """
        SSH into the development box.
        """

        # Change into the vagrant folder
        self.cd_into_vagrant() 

        # Try to ssh into the vagrant box
        try: 
            result = subprocess.check_call(['vagrant', 'ssh'])
        except subprocess.CalledProcessError as exception:
            message = """
                I could not ssh into the development box. 
                You could try navigating into the 
                `""" + self.data.vagrant_folder + """`
                folder and running the `vagrant ssh` command.
            """
            Utilities.show_error(message)

        # Get out of the vagrant folder
        self.cd_out_of_vagrant()



#########################################################
#########################################################
# A cli 

class Cli(cmd.Cmd):
    """
    The CLI for this program.
    """

    # Available commands in textual format
    commands = {
        'spinup': '-- `spinup` to spin up your dev box.',
        'spindown': '-- `spindown` to shut down your dev box.',
        'ssh': '-- `ssh` to ssh into your dev box.',
        'help-command': '-- `help <command>` for help on a specific command',
        'help': '-- `help` for a list of all commands',
        'exit': '-- `exit` to quit'
    }

    # The initial intro text that shows when the program starts up.
    intro =  '\n'
    intro += '\n'
    intro += '\n'
    intro += '*********************************************\n'
    intro += '\n'
    intro += '   Welcome to Spinup.\n' 
    intro += '   What would you like to do?\n\n'
    intro += '---------------------------------------------\n'
    intro += '\n'

    # The prompt 
    prompt = '>> '


    def cmdloop(self, intro=None):
        """
        Displays some intro text, then starts the command line prompt.
        """
        intro =  self.intro
        intro += self.show_commands()
        return cmd.Cmd.cmdloop(self, intro)


    def show_commands(self, omit=[]):
        """
        Display the available commands, optionally omitting some.
        """ 
        commands = ''
        for command in self.commands:
            if command not in omit:
                commands += self.commands[command] + '\n'
        return commands


    def register_data(self, data):
        """
        Initializes the Cli by storing some data.
        """
        self.data = data


    def default(self, text):
        """
        Runs when a command is not recognized.
        """
        message = 'Sorry, I don\'t recognize that command.'
        print message


    def help_help(self):
        """
        The `help` command lists all commands. 
        Type `help foo` (or equivalently `? foo`) 
        for instructions about the `foo` command.
        """
        message =  '\n'
        message += '        Type `help` to see a list of all commands.\n'
        message += '        Type `help foo` (or equivalently `? foo`) '
        message += 'to see\n        instructions for the command `foo`.\n'
        print message


    def do_exit(self, text): 
        """
        The `exit` command quits the spinup program.
        """
        message = 'Exiting...Goodbye.'
        print message
        return True


    def do_spinup(self, text):
        """
        The `spinup` command boots up a
        development server for you to use.
        """

        # Parse any arguments passed to this command
        passed_arguments = text.split()
        arguments = {}
        for argument in passed_arguments:
            argument_parts = argument.split('=')
            argument_name = argument_parts[0][2:]
            argument_value = argument_parts[1]
            arguments[argument_name] = argument_value

        # Run setup
        self.data.installer.setup()

        # Spin up the dev environment
        self.data.spinner.spinup(arguments=arguments)

        # List the commands again (minus `spinup`)
        print self.show_commands(omit=['spinup'])


    def do_spindown(self, text):
        """
        The `spindown` command shuts down a
        development server.
        """

        # Spin down the dev environment
        self.data.spinner.spindown()

        # List the commands again (minus `spindown`)
        print self.show_commands(omit=['spindown'])


    def do_ssh(self, text):
        """
        The `ssh` command SSHs into the development VM.
        """

        # SSH into the dev box
        self.data.spinner.ssh()

        # List the commands again
        print '\n'
        print '*************************************'
        print '\n'
        print self.show_commands(omit=['spinup'])



#########################################################
#########################################################
# Get some data about the user's system

# Get the operating system.
operating_system = platform.system()
if not operating_system:
    message = """
        I could not determine what kind of operating
        system you are using. Unfortunately,  
        I can't spin up a development server for 
        you. Sorry!  
    """
    Utilities.show_error(message)

# Lowercase the operating system name (for convenience).
else:
    Data.os = operating_system.lower()

# Get the architecture of this machine.
Data.architecture = platform.machine()

# Is this a 32 or 64 bit system?
Data.is_64bits = sys.maxsize > 2**32

# Get the linux distribution
Data.linux_distribution = platform.linux_distribution()

# Get the current working directory.
Data.cwd = os.path.abspath(os.getcwd())




#########################################################
#########################################################
# Initialize and start up the program

# Instantiate the installer.
installer = Installer(Data)
Data.installer = installer

# Instantiate the setup tool.
setup = Setup(Data)
Data.setup = setup

# Instantiate the provisioner.
provisioner = Provisioner(Data)
Data.provisioner = provisioner

# Instantiate the spinner
spinner = Spinner(Data)
Data.spinner = spinner

# Run the command line interpreter.
cli = Cli()
Data.cli = cli
cli.register_data(Data)
cli.cmdloop()

exit()
