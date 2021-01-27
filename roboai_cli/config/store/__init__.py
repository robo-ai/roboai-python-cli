from os.path import join

from .utils import getConfigDir, createConfig, loadConfigs, getConfigSize, \
    getConfigs, setConfigs, hasConfigs, deleteConfigs, clearConfigs


class ConfigStore:

    def __init__(self, name, defaults={}, globalConfigPath=False):
        self.name = name
        self.defaults = defaults
        self.globalConfigPath = globalConfigPath

        self.configDir = getConfigDir()

        if self.globalConfigPath:
            self.pathPrefix = join(name, 'config.json')
            pathEntry = name
        else:
            self.pathPrefix = join('configstore', '{}.json'.format(name))
            pathEntry = 'configstore'

        self.path = join(self.configDir, self.pathPrefix)
        # self.all = {}
        createConfig(self.path, self.defaults, pathEntry=pathEntry)
        self.Object = loadConfigs(self.path)
        self.size = getConfigSize(self.path)

    def all(self, Object=None):
        if Object:
            self.set(Object)

        jsonConfigs = loadConfigs(self.path)
        return jsonConfigs

    def get(self, key):
        value = getConfigs(self.path, key)
        return value

    def set(self, key, value=None):
        if isinstance(key, dict):
            setObject = key
            setConfigs(self.path, Object=setObject)
        else:
            setConfigs(self.path, key=key, value=value)

    def has(self, key):
        return hasConfigs(self.path, key)

    def delete(self, key):
        deleteConfigs(self.path, key)

    def clear(self):
        clearConfigs(self.path)
