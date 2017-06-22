"""

 Summary:
     Contains tools used to calculate geoemtric properties, such as polygon
     area and perimiter.

 Author:
     Duncan Runnacles

  Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

def polygonArea(xy_vals):
    """Calculate the area of an irregular polygon.

    Args:
        xy_vals(list): containing a tuple in each element with the x and y
            values for the geometry data.

    Return:
        double - the area of the polygon.
    """
    n = len(xy_vals)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += xy_vals[i][0] * xy_vals[j][1]
        area -= xy_vals[j][0] * xy_vals[i][1]
    area = abs(area) / 2.0
    return area