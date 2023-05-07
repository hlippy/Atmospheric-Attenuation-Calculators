from BilinearInterpolation  import BilinearInterpolation

def compute_rain_height(directory, lat, lon, logging):
    '''
    Compute the mean annual rain height above sea level from the 0 degree C
    isotherm.

    REFERENCE: ITU Recommendation ITU-R P.839-4 (in force as of SEP 2013)

    INPUT PARAMETERS:
        directory : location of the text files containing the 0 degree C
                    isotherm data, supplied by the ITU with ITU-R P.839-4
        lat       : latitude of the desired location (N)
        lon       : longitude of the desired location (E)

    OUTPUT PARAMETER:
        h_R       : mean annual height above sea level from the 0 degree C
                    isotherm (km)
    '''

    lat_dir = directory + 'Lat.txt'
    lon_dir = directory + 'Lon.txt'
    h0_dir  = directory + 'h0.txt'
    directories = {
        'Lat': lat_dir,
        'Lon': lon_dir,
        'Target': h0_dir
    }

    return BilinearInterpolation(lat, lon, directories).interpolate() + 0.36
