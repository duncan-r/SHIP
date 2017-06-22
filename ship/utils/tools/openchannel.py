"""

 Summary:
     Contains methods for calculating characteristics of open channel flow.

     Currently only used to calculate conveyance for a channel section.

 Author:
     Duncan Runnacles

  Created:
     01 Apr 2016

 Copyright:
     Duncan Runnacles 2016

 TODO:

 Updates:

"""

import math

import logging
logger = logging.getLogger(__name__)

import ship.utils.utilfunctions as utilfunc


def interpolateGaps(y_vals, space):
    """ Fill in any large gaps in the depths list

    Args:
        y_vals(list): elevation values.
        space(float): maximum allowable difference between interpolation values.

    Return:
        list of new y values to calculate conveyance for.
    """

    depths = sorted(y_vals)
    location = len(y_vals) - 1
    while location > 0:
        diff = depths[location] - depths[location-1]
        if diff > space:
            no_insert = int(diff / space)

            for j in range(0, no_insert):
                baseline = depths[location]
                depths.insert(location, baseline - space)
            location -= 1
        else:
            location -= 1

    return depths


def calcConveyance(x_vals, y_vals, panel_vals=[], n_vals=None, depths=[],
                        no_panels=False, interpolate_space=0, tolerance=0.0):
    """Calculate conveyance over a range of depths from min to max elevation.

    Args:
        x_vals(list): cross section chainage values.
        y_vals(list): corresponding elevation values
        panel_vals=[](list): corresponding panel locations.
        n_vals=[](list): corresponding mannings n values.
        depths=[](list): list of depths required. Any specific depths needed.
        no_panels(Bool): If false any panels found will not be included
            in the calculations.
        interpolate_space=0(int): float stipulating the maximum allowable space
            between depths. If zero then only section elevations will be used.
        tolerance=0.0(float): tolerance used to identify negative conveyance.
            if the reduction in conveyance is less than tolerance it will not
            be flagged.

    Return:
        Tuple:
            list: containing a dictionary for each depth with:
                Conveyance: the conveyance value calculated.
                Stage: the depth of the value calculated.
                Negative: boolean - True if value less than previous depth.
            boolean: True if contains a negative conveyance.
    """

    def checkVars(x_vals, n_vals, depths):
        """Check variables before running.

        If n_vals elements are None they will be replaced with the default
        value of 0.04.

        Args:
            x_vals(list): cross section chainage values.
            n_vals=[](list): corresponding mannings n values.
            depths=[](list): list of depths required. Any specific depths needed.

        Return:
            tuple: depths(list), roughness(list)
        """
        if len(depths) < 1:
            depths = sorted(y_vals)

        if interpolate_space > 0:
            depths = interpolateGaps(y_vals, interpolate_space)
        else:
            depths = sorted(y_vals)

        # If not n vals supplied set up some defaults
        if not isinstance(n_vals, list):
            if not n_vals == None:
                n_vals= [n_vals] * len(x_vals)
            else:
                n_vals = [0.04] * len(x_vals)

        return depths, n_vals


    def buildSections(x_vals, y_vals, n_vals, panel_vals, no_panels):
        """Create the section setups needed based on the inputs

        Args:
            x_vals(list): cross section chainage values.
            y_vals(list): corresponding elevation values
            n_vals=[](list): corresponding mannings n values.
            panel_vals=[](list): corresponding panel locations.
            no_panels(Bool): If false any panels found will not be included
                in the calculations.

        Return:
            list of all of the panel section data as tuple(x(list), y(list),
                n(list)).
        """

        all_sections = []

        # If there's only one panel wanted only create one section from all
        # of the data provided. Otherwise create multiple sections split on
        # panel markers indices
        if len(panel_vals) < 1 or no_panels == True:
                x_arr = x_vals
                y_arr = y_vals
                n_arr = n_vals
                all_sections.append([x_arr, y_arr, n_arr])

        else:
            indices = [i for i, x in enumerate(panel_vals) if x == True]
            start = 0
            for i in indices:
                x_arr = x_vals[start:i+1]
                y_arr = y_vals[start:i+1]
                n_arr = n_vals[start:i]
                all_sections.append([x_arr, y_arr, n_arr])
                start = i

            x_arr = x_vals[start:]
            y_arr = y_vals[start:]
            n_arr = n_vals[start:]
            all_sections.append([x_arr, y_arr, n_arr])

        return all_sections


    def calcSectionK(section, depth):
        """Calculate conveyance (K) for each section at the given depth.

        section is a list of tuples containing the data for each section of
        channel geometry in the cross section (i.e. each set of two x and y
        points and their associated roughness value).

        Args:
            section(list): containing variables for this geometrical section.
            depth(float): the depth below which to calculate conveyance.

         Return:
            Dict: containing lists of area, wp and n * wp

        """
        panel_data = {'area': [], 'wp': [], 'nxwp': []}

        def addToPanel(area, wp, nxwp):
            """Add calculated values to panel list
            """
            panel_data['area'].append(area)
            panel_data['wp'].append(wp)
            panel_data['nxwp'].append(nxwp)

        # Loop through each of the channel data sections (i.e. the sets of
        # x's) and calculate K for the piece. Then add to the panel list.
        for i in range(1, len(section[0])):

            x1 = section[0][i]
            x2 = section[0][i-1]
            y1 = section[1][i]
            y2 = section[1][i-1]
            n = section[2][i-1]

            miny, maxy, same_val = utilfunc.findMax(y1, y2)

            # Water level lower than min elevation so no K
            if depth < miny:
                addToPanel(0, 0, 0)

            else:
                height = maxy - miny
                width = abs(x1-x2)

                # Need to scale the triangle because the depth is lower than
                # the top of the x/y triangle. Reduce x by the same factor as
                # we're reducing y.
                if depth < maxy:
                    height2 = depth - miny
                    width = width * (height2 / height)
                    height = height2
                    maxy = depth

                # If the y vals are the same then wp is just the difference
                # between the x values, and the flow area contributed to by the
                # difference in y is 0. otherwise it's the hypotenus and the
                # area is taken from the triangle.
                if same_val:
                    wp = width
                    area = 0
                else:
                    wp = math.sqrt(height**2.0 + width**2.0)
                    area = ((height * width) / 2)

                # flow above it to area.
                if maxy < depth:
                    area += ((depth - maxy) * width)

                # Finally calculate mannings x wetted perimiter and add to the
                # panel calcs list.
                nxwp = n * wp
                addToPanel(area, wp, nxwp)
                #print 'Stage = %f  :  Area = %f  :  WP = %f  :  NxWP = %f' % (depth, area, wp, nxwp)
        return panel_data


    depths, n_vals = checkVars(x_vals, n_vals, depths)
    all_sections = buildSections(x_vals, y_vals, n_vals, panel_vals, no_panels)

    # Loop through the depths calculating K and add the sum af the conveyance
    # from each panel together and put results in a list to return to the
    # calling function.
    results = []
    has_negative = False
    previous_k = -1
    for d in depths:
        total_k = []

        # There could be one panel or many so loop through them all at each
        # depth calc and calculate flow area and wetted perimiter for each
        # x/y pair before using to calculate conveyance.
        for section in all_sections:

            panel_data =  calcSectionK(section, d)
            total_area = sum(panel_data['area'])
            total_wp = sum(panel_data['wp'])
            total_nxwp = sum(panel_data['nxwp'])

            if not total_wp == 0.0:
                panel_k = ( (total_area**5.0 / total_wp**2.0 )**(1.0/3.0) ) * ( total_wp / total_nxwp )
                #print 'Panel totals'
                #print 'Stage = %f  :  Area = %f  :  WP = %f  :  NxWP = %f' % (d, total_area, total_wp, total_nxwp)
            else:
                panel_k = 0.0

            total_k.append(panel_k)

        negative = False
        depth_k = sum(total_k)
        if not previous_k == -1 and previous_k > depth_k:
            if (previous_k - depth_k) > tolerance:
                negative = True
                has_negative = True
        previous_k = depth_k

        results.append([depth_k, d, negative])
        #print 'Depth Totals'
        #print 'Conveyance at depth: %f  =  %f\n' % (d, depth_k)

    return results, has_negative



