import math
import os

class BilinearInterpolation:
    def __init__(self, lat, lon, directories, convert_to_west = True):
        '''
        Constructor
        '''
        
        self.lat         = lat
        self.lon         = lon

        # Do we need to convert to west longitude?
        self.convert_to_west = convert_to_west

        # Paths to the files with the provided data
        self.lat_dir     = directories["Lat"]
        self.lat_fp      = -1
        self.lon_dir     = directories["Lon"]
        self.lon_fp      = -1
        self.target_dir  = directories["Target"]
        self.target_fp   = -1

        # Matrix dimensions
        self.row_count   = -1
        self.col_count   = -1

        # Matrix data
        self.lat_data    = -1
        self.lon_data    = -1
        self.target_data = -1

        # Matrix of distances from grid points to desired lat/lon
        self.distances   = []

    def open_files(self):
        '''
        Open the files
        '''

        self.lat_fp    = open(self.lat_dir, 'r')
        self.lon_fp    = open(self.lon_dir, 'r')
        self.target_fp = open(self.target_dir, 'r')

    def close_files(self):
        '''
        Close the files
        '''

        self.lat_fp.close()
        self.lon_fp.close()
        self.target_fp.close()

    def reset_files(self):
        '''
        Rese the file pointers to beginning of the files
        '''

        self.lat_fp.seek(0)
        self.lon_fp.seek(0)
        self.target_fp.seek(0)

    def get_matrix_dimensions(self):
        '''
        Get the number of rows and columns, and make sure they are the same
        for all file types.
        '''

        # Do a count of the number of rows and columns in the data. Do a cross-
        # check to make sure all three matrices are the same dimensions.

        lat_row_count    = len(self.lat_fp.readlines())
        lon_row_count    = len(self.lon_fp.readlines())
        target_row_count = len(self.target_fp.readlines())

        self.reset_files()
        
        row_count, col_count = -1, -1
        
        if lat_row_count + lon_row_count + target_row_count == 3*lat_row_count:
            self.row_count = lat_row_count
    
            lat_row    = [float(x) for x in self.lat_fp.readline().split()]
            lon_row    = [float(x) for x in self.lon_fp.readline().split()]
            target_row = [float(x) for x in self.target_fp.readline().split()]

            if len(lat_row) + len(lon_row) + len(target_row) == 3*len(lat_row):
                self.col_count = len(lat_row)
            else:
                row_error = 'Col count differs across files!' + os.linesep() +\
                            '    Lat = ' + str(len(lat_row)) + os.linesep() +\
                            '    Lon = ' + str(len(lon_row)) + os.linesep() +\
                            '    Target = ' + str(len(target_row))
                raise ValueError(col_error)        
        else:
            row_error = 'Row count differs across files!' + os.linesep() +\
                        '    Lat = ' + str(lat_row_count) + os.linesep() +\
                        '    Lon = ' + str(lon_row_count) + os.linesep() +\
                        '    Target = ' + str(target_row_count)
            raise ValueError(row_error)

        self.reset_files()
                 
    def read_data(self):
        '''
        Read the data from the filie into 2D matrices
        '''
        
        # Read in the provided data into three separate matrices
        self.lat_data = [[0 for _ in range(self.col_count)]\
                            for _ in range(self.row_count)]
        self.lon_data = [[0 for _ in range(self.col_count)]\
                            for _ in range(self.row_count)]
        self.target_data = [[0 for _ in range(self.col_count)]\
                               for _ in range(self.row_count)]

        row = 0
        while True:
            lat_raw    = self.lat_fp.readline()
            lon_raw    = self.lon_fp.readline()
            target_raw = self.target_fp.readline()

            if not (lat_raw and lon_raw and target_raw):
                break

            # Convert the string values into floats
            # NOTE: longitude conversion reference: https://tinyurl.com/2s9hrnux
            lat = [float(x) for x in lat_raw.split()]
            if self.convert_to_west:
                lon = [((float(x)+180.0)%360.0)-180.0 for x in lon_raw.split()]
            else:
                lon = [float(x) for x in lon_raw.split()]
            target = [float(x) for x in target_raw.split()]
    
            for col in range(len(lat)):
                self.lat_data[row][col]    = lat[col]
                self.lon_data[row][col]    = lon[col]
                self.target_data[row][col] = target[col]

            row = row + 1

    def compute_distances(self):
        '''
        Compute the distances from the requested lat/lon position to each of
        the grid points, and sort ascending so that the closest grid point is
        at the beginning of the list
        '''

        for row in range(self.row_count):
            for col in range(self.col_count):
                self.distances.append(tuple((
                    row,
                    col,
                    math.sqrt(
                        (self.lat_data[row][col] - self.lat)**2 +\
                        (self.lon_data[row][col] - self.lon)**2))))

        # Sort the list of tuples by the third element (which is the distance)
        self.distances.sort(key = lambda x:x[2])

    def interpolate(self):
        '''
        Perform a bilinear interpolation using 4 points on bounding box that
        has the nearest point to the gound station as one corner. If the
        requested lat/lon falls on a grid point, just return the target data
        value at that point.

        NOTE: Equations and variable names come from:
                  https://en.wikipedia.org/wiki/Bilinear_interpolation
        '''

        # Read in the data and compute the distances from the requested lat/lon
        # to each of the grid points
        self.open_files()
        self.get_matrix_dimensions()
        self.read_data()
        self.close_files()
        self.compute_distances()
        
        if self.distances[0][2] == 0.0:
            res = self.target_data[self.distances[0][0]][self.distances[0][1]]
        else:
            # Get lat/lon data for the closest point
            row, col = self.distances[0][0], self.distances[0][1]
            closest  = tuple((self.lat_data[row][col], self.lon_data[row][col]))

            # Define variables using bounding box defined by the closest grid point
            if closest[0] < self.lat and closest[1] < self.lon:
                # Closest grid point is lower-left corner of the bounding box
                x1   = self.lat_data[row][col]
                y1   = self.lon_data[row][col]
                x2   = self.lat_data[row-1][col+1]
                y2   = self.lon_data[row-1][col+1]
                fQ11 = self.target_data[row][col]
                fQ21 = self.target_data[row][col+1]
                fQ12 = self.target_data[row-1][col]
                fQ22 = self.target_data[row-1][col+1]
            elif closest[0] < self.lat and closest[1] > self.lon:
                # Closest grid point is lower-right corner of the bounding box
                x1   = self.lat_data[row][col-1]
                y1   = self.lon_data[row][col-1]
                x2   = self.lat_data[row-1][col]
                y2   = self.lon_data[row-1][col]
                fQ11 = self.target_data[row][col-1]
                fQ21 = self.target_data[row][col]
                fQ12 = self.target_data[row-1][col-1]
                fQ22 = self.target_data[row-1][col]
            elif closest[0] > self.lat and closest[1] < self.lon:
                # Closest grid point is top-left corner of the bounding box
                x1   = self.lat_data[row+1][col]
                y1   = self.lon_data[row+1][col]
                x2   = self.lat_data[row][col+1]
                y2   = self.lon_data[row][col+1]
                fQ11 = self.target_data[row+1][col]
                fQ21 = self.target_data[row+1][col+1]
                fQ12 = self.target_data[row][col]
                fQ22 = self.target_data[row][col+1]
            else:
                # Closest grid point is top-right corner of the bounding box
                x1   = self.lat_data[row+1][col-1]
                y1   = self.lon_data[row+1][col-1]
                x2   = self.lat_data[row][col]
                y2   = self.lon_data[row][col]
                fQ11 = self.target_data[row+1][col-1]
                fQ21 = self.target_data[row+1][col]
                fQ12 = self.target_data[row][col+1]
                fQ22 = self.target_data[row][col]

            # Perform the interpolation
            res = 1.0 / ((x2-x1)*(y2-y1)) *\
                 (fQ11*(x2-self.lat)*(y2-self.lon) +\
                  fQ21*(self.lat-x1)*(y2-self.lon) +\
                  fQ12*(x2-self.lat)*(self.lon-y1) +\
                  fQ22*(self.lat-x1)*(self.lon-y1))

        return res

        
