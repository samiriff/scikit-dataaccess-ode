# The MIT License (MIT)
# Copyright (c) 2018 Massachusetts Institute of Technology
#
# Author: Guillaume Rongier
# This software has been created in projects supported by the US National
# Science Foundation and NASA (PI: Pankratius)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Scikit Data Access imports
from skdaccess.framework.data_class import DataFetcherCache, ImageWrapper
from skdaccess.utilities.ode_util import *

# 3rd party imports
import matplotlib.image as mpimg
from tqdm import tqdm

# Standard library imports
from collections import OrderedDict


class DataFetcherMini(DataFetcherCache):
    ''' Data Fetcher from the Orbital Data Explorer (ODE) '''

    def __init__(self, target, mission, instrument, product_type,
                 western_lon=None, eastern_lon=None, min_lat=None, max_lat=None,
                 min_ob_time='', max_ob_time='', product_id='', file_name='*',
                 number_product_limit=10, result_offset_number=0, remove_ndv=True):

        '''
        Construct Data Fetcher object
        For more information about the different fields and the possible values,
        see the manual of ODE REST interface at http://oderest.rsl.wustl.edu
        @param target: Aimed planetary body, i.e., Mars, Mercury, Moon, Phobos, or Venus
        @param mission: Aimed mission, e.g., MGS or MRO
        @param instrument: Aimed instrument from the mission, e.g., HIRISE or CRISM
        @param product_type: Type of product to look for, e.g., DTM or RDRV11
        @param western_lon: Western longitude to look for the data, from 0 to 360
        @param eastern_lon: Eastern longitude to look for the data, from 0 to 360
        @param min_lat: Minimal latitude to look for the data, from -90 to 90
        @param max_lat: Maximal latitude to look for the data, from -90 to 90
        @param min_ob_time: Minimal observation time in (even partial) UTC format, e.g., '2017-03-01'
        @param max_ob_time: Maximal observation time in (even partial) UTC format, e.g., '2017-03-01'
        @param product_id: PDS Product ID to look for, with wildcards (*) allowed
        @param file_name: File name to look for, with wildcards (*) allowed
        @param number_product_limit: Maximal number of products to return (ODE allows 100 at most)
        @param result_offset_number: Offset the return products, to go beyond the limit of 100 returned products
        @param remove_ndv: Replace the no-data value as mentionned in the label by np.nan
        '''

        assert western_lon is None or 0. <= western_lon <= 360., 'Western longitude is not between 0 and 360 degrees'
        assert eastern_lon is None or 0. <= eastern_lon <= 360., 'Eastern longitude is not between 0 and 360 degrees'
        assert min_lat is None or -90. <= min_lat <= 90., 'Minimal latitude is not between -90 and 90 degrees'
        assert max_lat is None or -90. <= max_lat <= 90., 'Maximal latitude is not between -90 and 90 degrees'
        assert 1 <= number_product_limit <= 100, 'Number of product limit must be between 1 and 100'

        self.target = target
        self.mission = mission
        self.instrument = instrument
        self.product_type = product_type
        self.western_lon = western_lon
        self.eastern_lon = eastern_lon
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_ob_time = min_ob_time
        self.max_ob_time = max_ob_time
        self.product_id = product_id
        self.file_name = file_name
        self.number_product_limit = number_product_limit
        self.result_offset_number = result_offset_number
        self.remove_ndv = remove_ndv
        self.limit_file_types = 'Browse';

    def output(self):
        '''
        Generate data wrapper from ODE data
        '''
        file_urls = query_files_urls(self.target, self.mission, self.instrument, self.product_type,
                                     self.western_lon, self.eastern_lon, self.min_lat, self.max_lat,
                                     self.min_ob_time, self.max_ob_time, self.product_id, self.file_name,
                                     self.number_product_limit, self.result_offset_number, self.limit_file_types)

        downloaded_files = self.cacheData('ode', file_urls.keys())

        # Gather the data and meta-data
        data_dict = OrderedDict()
        # print("File Urls = ", file_urls)
        for file, key in tqdm(zip(downloaded_files, file_urls.keys())):
            if file.endswith('.jpg') or file.endswith('.png'):
                file_description = file_urls.get(key)[1]
                # print("File description = ", file_description)
                # print("Product = ", file_urls.get(key)[0])
                product = file_urls.get(key)[0]
                # print("File = ", file)
                if data_dict.get(product, None) is None:
                    data_dict[product] = OrderedDict()
                data_dict[product][file_description] = mpimg.imread(file)

        # print("data dict = ", data_dict)
        print("Processing complete")

        return ImageWrapper(obj_wrap=data_dict)
