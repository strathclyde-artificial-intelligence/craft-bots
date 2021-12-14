import yaml

class Configuration:

    # ================= #
    # reading ini files #
    # ================= #

    @classmethod
    def read_ini_file(cls, path):
        parameters = {}
        with open(path, "r") as stream:
            try:
                parameters = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return parameters

    # ================== #
    # easy config access #
    # ================== #

    @classmethod
    def get_value(cls, configuration, key):
        for category,config in configuration.items():
            if key in config:
                return config[key]['value']
        print("Get config key not found: ",key)
        return None

    @classmethod
    def set_value(cls, configuration, key, value):
        for category,config in configuration.items():
            if key in config:
                config[key]['value'] = value
                return
        print("Set config key not found: ",key)
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