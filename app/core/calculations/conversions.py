def convert(value: int | float, src: str, dest: str) -> float:
    units = {'kWh', 'MWh', 'MJ', 'GJ', 'kg', 't', 'l', 'm3'}
# ERROR HANDLING
    if not isinstance(value, (int, float)):
        raise TypeError("Variable 'value' must be a number")

    if not isinstance(src, str) or not isinstance(dest, str):
        raise TypeError("Variables 'str' and 'dest' must be strings")

    if src not in units:
        raise ValueError(f"Variable 'src' has not allowed value. It must be one of: {units}")

    if dest not in units:
        raise ValueError(f"Variable 'dest' has not allowed value. It must be one of: {units}")

# UNIT CONVERSIONS
    if src == dest:
        return value
#                                          ENERGY
    elif src == 'MWh':                                  #from MWh
        if dest == 'kWh':
            return value * 1000
        elif dest == 'GJ':
            return value * 3.6
        elif dest == 'MJ':
            return value * 3600
    elif src == 'kWh':                                  #from kWh
        if dest == 'MWh':
            return value * 0.001
        elif dest == 'GJ':
            return value * 0.0036
        elif dest == 'MJ':
            return value * 3.6
    elif src == 'GJ':                                   #from GJ
        if dest == 'kWh':
            return value * 1000 / 3.6
        elif dest == 'MWh':
            return value / 3.6
        elif dest == 'MJ':
            return value * 1000
    elif src == 'MJ':                                   #from MJ
        if dest == 'kWh':
            return value / 3.6
        elif dest == 'MWh':
            return value / 3600
        elif dest == 'GJ':
            return value / 1000
#                                           WEIGHT
    elif src == 'kg':                                   #from kg
        if dest == 't':
            return value / 1000
    elif src == 't':                                    #from t
        if dest == 'kg':
            return value * 1000
#                                           VOLUME
    elif src == 'l':                                    #from l
        if dest == 'm3':
            return value *0.001
    elif src =='m3':                                    #from m3
        if dest == 'l':
            return value * 1000





