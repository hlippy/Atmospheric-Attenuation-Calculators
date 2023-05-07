from BilinearInterpolation import BilinearInterpolation

def compute_rainfall_rate(directory, p, lat, lon, logging):

    '''
    Compute the rainfall exceed for a given average annual probability of
    exceedance and a given location on the surface of the Earth using digital
    maps of monthly total rainfall and monthly mean surface temperature.

    REFERENCE: ITU Recommendation ITU-R P.837-7 (in force as of 20 APR 2023)

    INPUT PARAMETERS:
        directory : location of the text files containing the rainfall and
                    surface temperature data, supplied by the ITU with
                    ITU-R P.837-7
        p         : desired probability of exceedance (%)
        lat       : latitude of the desired location (N)
        lon       : longitude of the desired location (E)

    OUTPUT PARAMETER:
        R_p       : rainfall rate exceed for the desired probability of
                    exceedance (mm/h)
    '''

    lat_dir = directory + 'LAT_R001.TXT'
    lon_dir = directory + 'LON_R001.TXT'
    R001_dir = directory + 'R001.TXT'
    directories = {
        'Lat': lat_dir,
        'Lon': lon_dir,
        'Target': R001_dir
    }

    return BilinearInterpolation(lat, lon, directories, False).interpolate()
