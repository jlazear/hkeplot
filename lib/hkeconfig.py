import ConfigParser
import os


class HKEConfig(object):
    datadfl = '/Users/jlazear/github/hkeplot/'
    caldfl = ('/Users/jlazear/Documents/HDD Documents/Misc Data/Cal'
              ' Curves/')
    boardsdfl = ''
    configdefaults = {'hkeplot': {'datafolder': datadfl,
                                  'calfolder': caldfl,
                                  'boardsfolder': boardsdfl},
                      'loaded files': {}}

    def __new__(cls, filename='.hkeplot'):
        return cls.load_config_file(filename)

    @classmethod
    def load_config_file(cls, filename='.hkeplot'):
        """
        Load config file specified by filename.
        """
        config = ConfigParser.RawConfigParser()
        section = 'hkeplot'

        # Initialize configuration file if it doesn't exist
        if not os.path.isfile(filename):
            cls.write_config_file(cls.configdefaults, filename)

        config.read(filename)

        configdict = {}
        for section in config.sections():
            items = config.items(section)
            itemsdict = dict(items)
            configdict[section] = itemsdict

        return configdict

    @classmethod
    def initialize_config_file(cls, config, filename='.hkeplot'):
        """
        Initialize a config file. Useful if one does not already
        exist.
        """
        config.add_section('hkeplot')
        section = 'hkeplot'
        for key, value in cls.configdefaults.items():
            config.set(section, key, value)
        with open(filename, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def write_config_file(configdict, filename='.hkeplot'):
        """
        Write the configuration parameters in configdict to the
        file specified by filename.
        """
        config = ConfigParser.RawConfigParser()

        for section in configdict.keys():
            config.add_section(section)
            sectiondict = configdict[section]
            for item, value in sectiondict.items():
                config.set(section, item, value)

        with open(filename, 'w') as configfile:
            config.write(configfile)

    @classmethod
    def list_loaded_files(cls, filename='.hkeplot'):
        """
        Lists the loaded data files in the configuration file.
        """
        # Initialize configuration file if it doesn't exist
        if not os.path.isfile(filename):
            cls.write_config_file(cls.configdefaults, filename)

        config = ConfigParser.RawConfigParser()
        config.read(filename)

        loaded = config.items('loaded files')
        loaded = [pair[0] for pair in loaded]
        return loaded

    @classmethod
    def get_loaded_files(cls, filename='.hkeplot'):
        """
        Returns a dictionary of the loaded files and their
        corresponding load configurations.
        """
        # Initialize configuration file if it doesn't exist
        if not os.path.isfile(filename):
            cls.write_config_file(cls.configdefaults, filename)

        config = ConfigParser.RawConfigParser()
        config.read(filename)

        loaded = config.options('loaded files')

        retdict = {}
        for filename in loaded:
            fileconfig = dict(config.items(filename))
            retdict[filename] = fileconfig

        return retdict

    @classmethod
    def add_loaded_file(cls, filedict, configfname='.hkeplot',
                        name=None):
        """
        Adds a record of the specified loaded file into the specified
        configuration file.
        """
        # Initialize configuration file if it doesn't exist
        if not os.path.isfile(configfname):
            cls.write_config_file(cls.configdefaults, configfname)

        config = ConfigParser.RawConfigParser()
        config.read(configfname)

        f = filedict['file']
        absname = os.path.abspath(f.filename)
        shortname = os.path.basename(absname)
        if name is None:
            name = shortname

        config.set('loaded files', name, absname)
        sectionname = config.optionxform(name)
        try:
            config.add_section(sectionname)
        except ConfigParser.DuplicateSectionError:
            pass

        calfname = filedict['calfile']
        boardfname = filedict['boardsfile']
        tdict = filedict['temperature']
        taddress = tdict['address']
        tchannel = tdict['channel']
        dewar = filedict['dewar']
        desc = filedict['description']
        config.set(sectionname, 'temperature address', taddress)
        config.set(sectionname, 'temperature channel', tchannel)
        config.set(sectionname, 'description', desc)
        config.set(sectionname, 'dewar', dewar)
        config.set(sectionname, 'data file', absname)
        config.set(sectionname, 'cal file', calfname)
        config.set(sectionname, 'boards file', boardfname)
        config.set(sectionname, 'proper name', name)

        with open(configfname, 'w+') as configfile:
            config.write(configfile)

    @classmethod
    def remove_loaded_file(cls, name, configfname='.hkeplot'):
        """
        Removes a record of the specified loaded file into the
        specified configuration file.
        """
        if not os.path.isfile(configfname):
            cls.write_config_file(cls.configdefaults, configfname)

        config = ConfigParser.RawConfigParser()
        config.read(configfname)

        config.remove_option('loaded files', name)
        try:
            config.remove_section(name)
        except ConfigParser.NoSectionError:
            pass

        with open(configfname, 'w+') as configfile:
            config.write(configfile)
