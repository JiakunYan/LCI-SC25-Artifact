#!/usr/bin/env python3

import numpy as np

import math
def parse_tag(df, x_key, y_key, tag_key):
    lines = []

    for tag in df[tag_key].unique():
        criterion = (df[tag_key] == tag)
        df1 = df[criterion]
        current_domain = []
        current_value = []
        current_error = []
        for x in df1[x_key].unique():
            y = df1[df1[x_key] == x][y_key].mean()
            error = df1[df1[x_key] == x][y_key].std()
            if y is np.nan:
                continue
            if y == 0:
                continue
            current_domain.append(float(x))
            current_value.append(float(y))
            if math.isnan(error):
                error = 0
            current_error.append(float(error))
        lines.append({'label': str(tag), 'x': current_domain, 'y': current_value, 'error': current_error})
    return lines