from abc import ABC
from typing import Dict, Any, Union

import geopandas as gpd

import pandas as pd
from geopandas import GeoDataFrame
from pandas import DataFrame, Series
import os
import warnings


class GeoDataSetInfoError(Exception):

    def __init__(self, message="There was an error in the information given."):
        self.message = message
        super().__init__(self.message)


class GeoDataSetFrameReadError(Exception):

    def __init__(self, message="There was an error with reading the frame."):
        self.message = message
        super().__init__(self.message)


class GeoDataSetFrameError(Exception):

    def __init__(self, message="There was an error with the frame."):
        self.message = message
        super().__init__(self.message)


_valid_geo_fields = ['coord_field1', 'coord_field2', 'coord_field3', 'geometry']
_valid_analysis_fields = ['id_field', 'value_field']


def geodataframe_from_coordinates(df: DataFrame, z: bool = False, crs=None, to_crs=None) -> GeoDataFrame:
    """Takes a dataframe and converts it based on coordinate columns.

    :param df: The dataframe to convert
    :type df: DataFrame
    :param z: Whether there exists a third coordinate
    :type z: bool
    :param crs: The starting crs for this dataframe
    :type crs: str
    :param to_crs: Transform the geometry to the new crs
    :type to_crs: str
    :return: A GeoDataFrame (transformed or not)
    :rtype: GeoDataFrame
    """
    fields = (df['coord_field1'], df['coord_field2'])
    if z:
        fields += (df['coord_field3'])

    if to_crs:
        return GeoDataFrame(df, geometry=gpd.points_from_xy(*fields), crs=crs).to_crs(crs=to_crs)
    else:
        return GeoDataFrame(df, geometry=gpd.points_from_xy(*fields), crs=crs)


def geodataframe_from_geometry(df: DataFrame, crs=None, to_crs=None) -> GeoDataFrame:
    """Takes a dataframe and converts it based on geometry.

    :param df: The dataframe to convert
    :type df: DataFrame
    :param crs: The starting crs for this dataframe
    :type crs: str
    :param to_crs: Transform the geometry to the new crs
    :type to_crs: str
    :return: A GeoDataFrame (transformed or not)
    :rtype: GeoDataFrame
    """
    geodf = GeoDataFrame(df, geometry='geometry', crs=crs)
    if to_crs:
        if crs:
            geodf.to_crs(crs=to_crs, inplace=True)
        else:
            raise GeoDataSetInfoError("A beginning crs must be given to transform to a new crs!")
    return geodf


def read_geodataframe(value):
    """Reads a GeoDataFrame from a filepath.

    (Needs work)

    :param value: The string representing a filepath
    :type value: str
    :return: The read frame
    :rtype: GeoDataFrame
    """
    if value is None:
        raise GeoDataSetFrameError("You can not set frame to none!")

    # attempt to read the file as a DataFrame or GeoDataFrame
    if isinstance(value, str):
        # this means it could be a file path
        # attempt to read the file

        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, value)
        extension = os.path.splitext(filepath)[1]

        # we read csv files through pandas and then load them into a GeoDataFrame
        if extension == '.csv':
            return pd.read_csv(value)
        elif extension == '.shp':
            return gpd.read_file(value)
        elif os.path.isdir(filepath):
            # search for a shapefile in the path
            for item in os.listdir(filepath):
                if '.shp' in item:
                    return gpd.read_file(os.path.join(filepath, item))
                    break
            if not isinstance(value, GeoDataFrame):
                raise GeoDataSetFrameReadError('The file was not read properly!')
        else:
            warnings.warn(
                'The most common file formats are .csv, .shp, assuming that geopandas can properly read this file...')
            return gpd.read_file(value)
    raise GeoDataSetInfoError('The value is not a filepath.')


from collections.abc import MutableMapping


class GeoDataSet(dict):
    """This class provides an implementation of a GeoDataSet.

    A GeoDataSet is a dict-like object that contains a GeoDataFrame,
    and a list of columns that must be preserved.
    """

    def __init__(self, frame: Union[GeoDataFrame, DataFrame, str], fields: Dict[str, Any] = None, **kwargs):
        """Initializer for GeoDataSet.

        :param frame: The main GeoDataFrame in the dataset
        :type frame: Union[GeoDataFrame,DataFrame,str]
        :param fields: Fields to add to the dataset (important columns)
        :type fields: Dict[str, Any]
        :param kwargs: Fields to add to the dataset (important columns)
        :type kwargs: **kwargs
        """
        self._aliases = {'geometry': 'geometry'}
        self._persistent_fields = ['geometry']
        self._store = {}
        try:
            self._frame = read_geodataframe(frame)
        except GeoDataSetInfoError:
            self._frame = frame

        if fields:
            fields = fields.copy().update(kwargs)
            self._convert_fields(**fields)
        else:
            print('HERE')
            self._convert_fields(**kwargs)
        self._convert_geodataframe()

    def _convert_fields(self, **kwargs):
        """Takes a dictionary of important columns and stores them in the DataSet.

        :param kwargs: The important columns for this DataSet
        :type kwargs: **kwargs
        """

        for item in kwargs.items():
            self.__setitem__(item[0], item[1])

    def _convert_geodataframe(self):
        """Converts the internal frame into a valid GeoDataFrame.
        """

        value = self._frame

        c1_field, c2_field, c3_field, geometry_field = Series(), Series(), Series(), Series()
        try:
            c1_field = self._frame['coord_field1']
            c2_field = self._frame['coord_field2']
            c3_field = self._frame['coord_field3']
        except KeyError:
            pass

        try:
            print(self._frame.columns)
            print(self._frame)
            geometry_field = self._frame['geometry']
        except KeyError:
            pass

        crs = self.__dict__.get('crs', None)
        to_crs = self.__dict__.get('to_crs', None)

        if isinstance(value, GeoDataFrame):
            if not geometry_field.empty:
                if not c1_field.empty or not c2_field.empty or not c3_field.empty:
                    warnings.warn('Coordinate fields should not be passed with a geometry field. This process will '
                                  'continue assuming the geometry field takes precedence.')
                value = geodataframe_from_geometry(value, crs=crs)

            # is this part even necessary?
            elif (not c1_field.empty and not c2_field.empty) or (
                    not c1_field.empty and not c2_field.empty and not c3_field.empty):
                if geometry_field is not None:
                    raise GeoDataSetInfoError('Geometry field should not be passed along with longitude and '
                                              'latitude fields.')
                value = geodataframe_from_coordinates(value, z=(not c3_field.empty), crs=crs)

        elif isinstance(value, DataFrame):
            try:
                value = geodataframe_from_coordinates(value, z=(not c3_field.empty), crs=crs)
            except KeyError:
                value = geodataframe_from_geometry(value, crs=crs)

        else:
            raise GeoDataSetFrameError("Your frame must be a valid GeoDataFrame!")

        if value.empty:
            raise GeoDataSetInfoError("The frame can not be empty!")

        if not value.crs:
            warnings.warn("A crs has not been set. This can be dangerous when performing spatial operations...")
        elif to_crs:
            value.to_crs(crs=to_crs, inplace=True)

        self._finalize_frame(value)

    def _finalize_frame(self, value):

        for item in self._aliases.items():
            if item[1] in value.columns:
                value.rename({item[1]: item[0]}, axis=1, inplace=True)

        self._frame = value
        self._store['frame'] = self._frame

    def isvalid(self):
        """Determines whether the GeoDataSet is valid or not.

        :return: True if valid otherwise False
        :rtype: bool
        """
        if self.frame is None or self.frame.empty:
            return False

        if not bool(self.__dict__):
            return False
        return True

    @property
    def frame(self):
        """Getter for internal frame.

        Returning a copy ensures that the frame can not be altered inplace.

        :return: A copy of the internal frame
        :rtype: GeoDataFrame
        """
        return self._frame.copy()

    @frame.setter
    def frame(self, value: Union[GeoDataFrame, DataFrame, str]):
        """Setter for internal frame.

        Checks if any persistent fields are still in the GeoDataFrame.

        :param value: The new frame
        :type value: Union[GeoDataFrame, DataFrame, str]
        """

        try:
            self._frame = read_geodataframe(value)
        except GeoDataSetInfoError:
            self._frame = value

        self._convert_geodataframe()
        for col in self._persistent_fields:
            if self._aliases[col] not in value.columns and col not in value.columns:
                raise GeoDataSetInfoError(f'A persistent column must stay constant when setting to a new frame. '
                                          f'The new frame does not have the persistent field {col}.')

    def __setattr__(self, key, value):
        if key in self.__dict__ and key not in ['_frame']:
            self.__setitem__(key, value)
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        return self._frame.__getitem__(item)

    def __getitem__(self, item):
        if item == 'frame':
            return self.frame
        try:
            return self.frame[item]
        except KeyError:
            return self.__dict__[item]

    def __setitem__(self, key, value):

        try:
            if value in self._frame.columns:

                if isinstance(value, tuple):
                    if isinstance(value[1], bool):
                        if value[1]:
                            self._persistent_fields.append(key)
                    else:
                        raise GeoDataSetInfoError("If you are adding a persistent field, the second argument should be a "
                                                  "bool.")
                    value = value[0]

                if key in self._frame.columns:
                    self._frame.rename({key: self._aliases[key]}, axis=1, inplace=True, errors='ignore')

                self._frame.rename({value: key}, axis=1, inplace=True, errors='raise')
                self._aliases[key] = value
            else:
                self._store[key] = value
                self.__dict__[key] = value
        except TypeError:
            self._store[key] = value
            self.__dict__[key] = value

    def __delitem__(self, key) -> None:
        del self._store[key]

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self):
        for key in self._store:
            yield key, self._store[key]

    def __str__(self):
        return str(self._store)

    def __contains__(self, item):
        return item in self._store
