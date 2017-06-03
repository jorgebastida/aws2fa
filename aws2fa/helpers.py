try:
    from ConfigParser import ConfigParser as DefaultConfigParser
    from ConfigParser import NoSectionError, DuplicateSectionError
except ImportError:
    from configparser import ConfigParser as DefaultConfigParser
    from configparser import NoSectionError, DuplicateSectionError


class ConfigParser(DefaultConfigParser):
    """
    Adaptation of python's ConfigParser.ConfigParser removing some limitations
    related to sections called 'default'.
    """

    def set(self, section, option, value=None):
        """Set an option."""
        try:
            sectdict = self._sections[section]
        except KeyError:
            raise NoSectionError(section)
        sectdict[self.optionxform(option)] = value

    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        """
        if section in self._sections:
            raise DuplicateSectionError(section)
        self._sections[section] = self._dict()
