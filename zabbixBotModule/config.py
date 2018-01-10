import yaml
import logging

class config:
    """
    load the config data
    """
    def __init__(self, section, configPath = 'config.cfg'):
        # load configure items
        with open(configPath, 'r') as ymlfile:
            completeData = yaml.load(ymlfile)

        try:
            self.loadedData = completeData[section]

        except:
            logging.error('Could not found the sections: %s in the config file: %s') % (section, configPath)

    def getConfigEntry(self, item={}, default=None):
        """
        Get the configuration, if not found return the default entry, if that is not set it will return an error.
        __getConfigEntry(self, item, default=None)

        """

        try:
            return self.loadedData[item]
        except:
            if default is not None:
                return default
            else:
                logging.error("%s not found in the config", item)
                exit(2)

    def dump(self):
        return self.loadedData
