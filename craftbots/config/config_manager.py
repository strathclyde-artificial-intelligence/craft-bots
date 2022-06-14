import yaml
import sys
from craftbots.log_manager import Logger


class Configuration:

    # ================= #
    # reading ini files #
    # ================= #

    @classmethod
    def read_ini_file(cls, path):
        parameters = {}
        try:
            with open(path, "r") as stream:
                try:
                    parameters = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    Logger.error("(config manager)", exc)
        except FileNotFoundError as exc:
            print(exc)
            sys.exit(-1)
        return parameters

    @classmethod
    def save_ini_file(cls, config, path):
        try:
            with open(path, "w") as file:
                try:
                    yaml.safe_dump(config,file)
                except yaml.YAMLError as exc:
                    Logger.error("(config manager)", exc)
        except IOError as exc:
            print(exc)

    # ================== #
    # easy config access #
    # ================== #

    @classmethod
    def get_value(cls, configuration, key):
        for category,config in configuration.items():
            if key in config:
                return config[key]['value']
        Logger.error("(config manager)", "Get config key not found: "+key)
        return None

    @classmethod
    def set_value(cls, configuration, key, value):
        # check for setting list value
        index = -1
        if "@" in key:
            index = int(key.split("@")[1])
            key = key.split("@")[0]
        for category,config in configuration.items():
            for k,v in config.items():
                # check sub-category
                if type(v)==dict and key in v:
                    if index >= 0: v[key][index] = value
                    else: v[key] = value
                    return
                # normal config property
                if key in config:
                    if index >= 0: config[key]['value'][index] = value
                    else:  config[key]['value'] = value
                    return
        Logger.error("(config manager)", "Set config key not found: "+key)
        return None

    @classmethod
    def flatten(cls, config):
        params = {}
        for key, value in config.items():
            if type(value)==dict and "value" in value:
                # default config item
                params[key] = value['value']
            elif type(value)==dict:
                # nested item
                for k,v in value.items(): params[k] = v
            else: params[key] = value
        return params