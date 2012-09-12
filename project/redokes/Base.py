class Base(object):
    config = {}
    def __new__(cls, config={}, *args, **kwargs):
        bases = cls.__bases__
        new_config = {}
        for base in bases:
            cls = super(cls.__class__, cls).__new__(cls)
            if hasattr(base, 'config'):
                new_config.update(base.config)
        new_config.update(cls.config)
        new_config.update(config)
        for key, value in new_config.items():
            setattr(cls, key, value)
        return cls