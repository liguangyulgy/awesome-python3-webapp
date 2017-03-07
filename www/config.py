__author__ = 'LiGuangyu'
import www.config_default as a

config = a.configs

def merge(a, b):
    rev = {}
    for k,v in a.items():
        if k in b:
            if isinstance(v,dict):
                rev[k] = merge(v,b[k])
            else:
                rev[k] = b[k]
        rev[k] = v
    return rev


try :
    from www.config_override import configs as b
    config = merge(config,b)
except ImportError:
    pass