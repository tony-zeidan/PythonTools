from typing import Tuple, List, Union, Dict, Optional
import palettable as pal
import numpy as np

ColorTuple = Tuple[int, ...]
ColorType = Tuple[int, ColorTuple]
ColorHelperType = List[ColorType]

def label_color(color: ColorTuple) -> str:
    """Provides a color string for the given color tuple.

    :param color: A tuple representing the components of a color
    :type color: ColorTuple
    :return: A string representing the given color
    :rtype: str
    """
    color_j = ','.join(str(v) for v in color)
    code_len = len(color)
    if code_len == 1:
        return f'#{color[0]}'
    elif code_len == 3:
        return f'rgb({color_j})'
    elif code_len == 4:
        return f'cmyk({color_j})'


def solid_scale(color: ColorTuple, min_scale: int = 0, max_scale: int = 1):
    """Retrieves a solid colorscale for a given color.

    :param color: The color to make a solid scale from
    :type color: ColorTuple
    :param min_scale: The minimum value on this colorscale
    :type min_scale: number
    :param max_scale: The maximum value on this colorscale
    :type max_scale: number
    :return: A solid colorscale
    :rtype: Tuple[Tuple[number, ColorTuple]]
    """
    return (min_scale, color), (max_scale, color)


def solid_scale_labels(color: ColorTuple, min_scale: int = 0, max_scale: int = 1):
    """Retrieves a solid colorscale for a given color.

    Colors are represented by strings.

    :param color: The color to make a solid scale from
    :type color: ColorTuple
    :param min_scale: The minimum value on this colorscale
    :type min_scale: number
    :param max_scale: The maximum value on this colorscale
    :type max_scale: number
    :return: A solid colorscale
    :rtype: Tuple[Tuple[number, str]]
    """
    first, second = solid_scale(color, min_scale=min_scale, max_scale=max_scale)
    return (first[0], label_color(first[1])), (second[0], label_color(second[1]))


def solid_scales(colors: List[ColorTuple], min_scale: int = 0, max_scale: int = 1):
    """Retrieves a list of solid colorscales.

    :param colors: The list of colors to retrieve solid colorscales for
    :type colors: List[ColorTuple]
    :param min_scale: The minimum value for each solid scale
    :type min_scale: number
    :param max_scale: The maximum value for each solid scale
    :type max_scale: number
    :return: A list of solid colorscales
    :rtype: List[Tuple[number,ColorTuple]]
    """
    return [solid_scale(color, min_scale, max_scale) for color in colors]


def solid_scales_labels(colors: List[ColorTuple], min_scale: int = 0, max_scale: int = 1):
    """Retrieves a list of solid colorscales.

    Colors are represented by strings.

    :param colors: The list of colors to retrieve solid colorscales for
    :type colors: List[ColorTuple]
    :param min_scale: The minimum value for each solid scale
    :type min_scale: number
    :param max_scale: The maximum value for each solid scale
    :type max_scale: number
    :return: A list of solid colorscales
    :rtype: List[Tuple[number,str]]
    """
    return [solid_scale_labels(color, min_scale, max_scale) for color in colors]


def get_colormap(source: str, *args):
    """Retrieves a colormap from the given source.

    :param source: The source to retrieve the colorscale from
    :type source: str
    :param args: Arguments to be passed into palettable.source.get_map()
    :type args: *args
    :return: A colormap
    :rtype: Palettable object
    """
    pal_source = getattr(pal, source)
    return pal_source.get_map(*args)


def colormap_solids(*args, **kwargs):
    """Retrieves a solid colormap of the source.

    :param args: Arguments to be passed into get_colormap()
    :type args: *args
    :param kwargs: Keyword arguments to be passed into solid_scales_labels()
    :type kwargs: **kwargs
    :return: A list of solid colorscales
    :rtype: List
    """
    return solid_scales(get_colormap(*args).colors, **kwargs)


def colormap_solids_labels(*args, **kwargs) -> List:
    """Retrieves a solid colormap of the source.

    Colorscales are represented with strings.

    :param args: Arguments to be passed into get_colormap()
    :type args: *args
    :param kwargs: Keyword arguments to be passed into solid_scales_labels()
    :type kwargs: **kwargs
    :return: A list of solid colorscales
    :rtype: List
    """
    return solid_scales_labels(get_colormap(*args).colors, **kwargs)


def all_scales(source:str, scale_type:Optional[str] = None) -> Dict:
    """Provides a dictionary of all colorscales in the given source.

    :param source: The source to retrieve the colorscales from
    :type source: str
    :param scale_type: The type of scale to retrieve
    :type scale_type: Optional[str]
    :return: A dictionary of colorscales
    :rtype: Dict
    """
    src = getattr(pal, source).COLOR_MAPS
    if scale_type is not None:
        src = src[scale_type]
    scales = {}
    for scheme in src.items():
        scheme_nums = scheme[1]
        max_num = max([int(num) for num in scheme_nums.keys()])
        selected = scheme_nums[str(max_num)]
        scales[scheme[0]] = (selected['Colors'])

    return scales


def all_scales_solid(*args, **kwargs) -> Dict:
    """Provides a dictionary of solid colorscales.

    This function takes all the colorscales located in the
    given source and turns them into solid colorscales.

    :param args: Arguments to be passed into all_scales()
    :type args: *args
    :param kwargs: Keyword arguments to be passed into solid_scales_labels()
    :type kwargs: **kwargs
    :return: A dictionary of all colorscales turned into solid colorscales
    :rtype: Dict
    """
    scale_type = kwargs.pop('scale_type',None)
    scales = all_scales(*args, scale_type=scale_type)
    scales_solid = {}
    for scale in scales.items():
        scales_solid[scale[0]] = solid_scales(scale[1], **kwargs)
    return scales_solid


def all_scales_solid_labels(*args, **kwargs) -> Dict:
    """Provides a dictionary of solid colorscales.

    This function takes all the colorscales located in the
    given source and turns them into solid colorscales.
    Colorscales are represented by strings.

    :param args: Arguments to be passed into all_scales()
    :type args: *args
    :param kwargs: Keyword arguments to be passed into solid_scales_labels()
    :type kwargs: **kwargs
    :return: A dictionary of all colorscales turned into solid colorscales
    :rtype: Dict
    """
    scales = all_scales(*args)
    scales_labels = {}
    for scale in scales.items():
        scales_labels[scale[0]] = solid_scales_labels(scale[1], **kwargs)
    return scales_labels


class ColorHelper:
    """This class provides a simple interface for the building of colorscales.
    """

    def __init__(self, colors: ColorHelperType = None):
        """Initializer for ColorHelper.

        :param colors: The colors to initialize the builder with
        :type colors: ColorHelperType
        """
        self._colors: ColorHelperType = []
        if colors is not None:
            self._colors = colors

    def add_color(self, color: ColorType):
        """Adds a color to the builder (assuming in proper form).

        :param color: The color to add
        :type color: ColorType
        """
        self._colors.append(color)

    def add_color_separate(self, num: Union[int, float], color: ColorTuple):
        """Adds a color by number and color tuple.

        :param num: A number representing this colors point on the scale
        :type num: Union[int, float]
        :param color: A tuple representing a color
        :type color: ColorTuple
        """
        self._colors.append((num, color))

    def load_colormap(self, min_scale: int, max_scale: int, *args):
        """Sets the colorscale of this builder to the loaded colorscale.

        This function sets the builders internals to that of the colorscale
        from the given source.

        :param min_scale: The smallest value on this colorscale
        :type min_scale: number
        :param max_scale: The largest value on this colorscale
        :type max_scale: number
        :param args: Arguments to be passed into get_colormap()
        :type args: *args
        """
        self._colors.clear()
        colors = get_colormap(*args).colors

        intervals = np.linspace(min_scale, max_scale, num=len(colors))
        for x in range(0, len(colors)):
            self.add_color_separate(intervals[x], colors[x])

    def get_colors(self) -> ColorHelperType:
        """Retrieves the colorscale in the builder.

        :return: The colorscale
        :rtype: ColorHelperType
        """
        return self._colors

    def get_color_labels(self) -> List[Tuple[int, str]]:
        """Retrieves the colorscale in the builder.

        Colors are represented with strings, not tuples.

        :return: The colorscale
        :rtype: List[Tuple[int, str]]
        """
        return [(color[0], label_color(color[1])) for color in self._colors]
