# config/config_handler.py
import configparser


class ConfigHandler:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        self.config.read(self.config_file)

    def get_config_option(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except (configparser.NoOptionError, configparser.NoSectionError):
            return default if default is not None else None

    def save_config(self):
        # Write the updated configuration to the file
        with open(self.config_file, 'w') as config_file:
            self.config.write(config_file)

    def set_config_option(self, section, option, value):
        # Set a configuration option in the specified section
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save_config()
