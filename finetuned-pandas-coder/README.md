---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:2039
- loss:MultipleNegativesRankingLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: Read text from clipboard and pass to :func:`~pandas.read_csv`.
  sentences:
  - "def is_platform_linux() -> bool:\n    \"\"\"\n    Checking if the running platform\
    \ is linux.\n\n    Returns\n    -------\n    bool\n        True if the running\
    \ platform is linux.\n    \"\"\"\n    return sys.platform == \"linux\""
  - "def read_clipboard(\n    sep: str = r\"\\s+\",\n    dtype_backend: DtypeBackend\
    \ | lib.NoDefault = lib.no_default,\n    **kwargs,\n):  # pragma: no cover\n \
    \   r\"\"\"\n    Read text from clipboard and pass to :func:`~pandas.read_csv`.\n\
    \n    Parses clipboard contents similar to how CSV files are parsed\n    using\
    \ :func:`~pandas.read_csv`.\n\n    Parameters\n    ----------\n    sep : str,\
    \ default '\\\\s+'\n        A string or regex delimiter. The default of ``'\\\\\
    s+'`` denotes\n        one or more whitespace characters.\n\n    dtype_backend\
    \ : {'numpy_nullable', 'pyarrow'}\n        Back-end data type applied to the resultant\
    \ :class:`DataFrame`\n        (still experimental). If not specified, the default\
    \ behavior\n        is to not use nullable data types. If specified, the behavior\n\
    \        is as follows:\n\n        * ``\"numpy_nullable\"``: returns nullable-dtype-backed\
    \ :class:`DataFrame`\n        * ``\"pyarrow\"``: returns pyarrow-backed nullable\n\
    \          :class:`ArrowDtype` :class:`DataFrame`\n\n        .. versionadded::\
    \ 2.0\n\n    **kwargs\n        See :func:`~pandas.read_csv` for the full argument\
    \ list.\n\n    Returns\n    -------\n    DataFrame\n        A parsed :class:`~pandas.DataFrame`\
    \ object.\n\n    See Also\n    --------\n    DataFrame.to_clipboard : Copy object\
    \ to the system clipboard.\n    read_csv : Read a comma-separated values (csv)\
    \ file into DataFrame.\n    read_fwf : Read a table of fixed-width formatted lines\
    \ into DataFrame.\n\n    Examples\n    --------\n    >>> df = pd.DataFrame([[1,\
    \ 2, 3], [4, 5, 6]], columns=[\"A\", \"B\", \"C\"])\n    >>> df.to_clipboard()\
    \  # doctest: +SKIP\n    >>> pd.read_clipboard()  # doctest: +SKIP\n         A\
    \  B  C\n    0    1  2  3\n    1    4  5  6\n    \"\"\"\n    encoding = kwargs.pop(\"\
    encoding\", \"utf-8\")\n\n    # only utf-8 is valid for passed value because that's\
    \ what clipboard\n    # supports\n    if encoding is not None and encoding.lower().replace(\"\
    -\", \"\") != \"utf8\":\n        raise NotImplementedError(\"reading from clipboard\
    \ only supports utf-8 encoding\")\n\n    check_dtype_backend(dtype_backend)\n\n\
    \    from pandas.io.clipboard import clipboard_get\n    from pandas.io.parsers\
    \ import read_csv\n\n    text = clipboard_get()\n\n    # Try to decode (if needed,\
    \ as \"text\" might already be a string here).\n    try:\n        text = text.decode(kwargs.get(\"\
    encoding\") or config[\"display\"][\"encoding\"])\n    except AttributeError:\n\
    \        pass\n\n    # Excel copies into clipboard with \\t separation\n    #\
    \ inspect no more than the 10 first lines, if they\n    # all contain an equal\
    \ number (>0) of tabs, infer\n    # that this came from excel and set 'sep' accordingly\n\
    \    lines = text[:10000].split(\"\\n\")[:-1][:10]  # pyright: ignore[reportOptionalSubscript]\n\
    \n    # Need to remove leading white space, since read_csv\n    # accepts:\n \
    \   #    a  b\n    # 0  1  2\n    # 1  3  4\n\n    counts = {x.lstrip(\" \").count(\"\
    \\t\") for x in lines}\n    if len(lines) > 1 and len(counts) == 1 and counts.pop()\
    \ != 0:\n        sep = \"\\t\"\n        # check the number of leading tabs in\
    \ the first line\n        # to account for index columns\n        index_length\
    \ = len(lines[0]) - len(lines[0].lstrip(\" \\t\"))\n        if index_length !=\
    \ 0:\n            kwargs.setdefault(\"index_col\", list(range(index_length)))\n\
    \n    elif not isinstance(sep, str):\n        raise ValueError(f\"{sep=} must\
    \ be a string\")\n\n    # Regex separator currently only works with python engine.\n\
    \    # Default to python if separator is multi-character (regex)\n    if len(sep)\
    \ > 1 and kwargs.get(\"engine\") is None:\n        kwargs[\"engine\"] = \"python\"\
    \n    elif len(sep) > 1 and kwargs.get(\"engine\") == \"c\":\n        warnings.warn(\n\
    \            \"read_clipboard with regex separator does not work properly with\
    \ c engine.\",\n            stacklevel=find_stack_level(),\n        )\n\n    return\
    \ read_csv(StringIO(text), sep=sep, dtype_backend=dtype_backend, **kwargs)"
  - "def to_clipboard(\n    obj, excel: bool | None = True, sep: str | None = None,\
    \ **kwargs\n) -> None:  # pragma: no cover\n    \"\"\"\n    Attempt to write text\
    \ representation of object to the system clipboard\n    The clipboard can be then\
    \ pasted into Excel for example.\n\n    Parameters\n    ----------\n    obj :\
    \ the object to write to the clipboard\n    excel : bool, defaults to True\n \
    \           if True, use the provided separator, writing in a csv\n          \
    \  format for allowing easy pasting into excel.\n            if False, write a\
    \ string representation of the object\n            to the clipboard\n    sep :\
    \ optional, defaults to tab\n    other keywords are passed to to_csv\n\n    Notes\n\
    \    -----\n    Requirements for your platform\n      - Linux: xclip, or xsel\
    \ (with PyQt4 modules)\n      - Windows:\n      - OS X:\n    \"\"\"\n    encoding\
    \ = kwargs.pop(\"encoding\", \"utf-8\")\n\n    # testing if an invalid encoding\
    \ is passed to clipboard\n    if encoding is not None and encoding.lower().replace(\"\
    -\", \"\") != \"utf8\":\n        raise ValueError(\"clipboard only supports utf-8\
    \ encoding\")\n\n    from pandas.io.clipboard import clipboard_set\n\n    if excel\
    \ is None:\n        excel = True\n\n    if excel:\n        try:\n            if\
    \ sep is None:\n                sep = \"\\t\"\n            buf = StringIO()\n\n\
    \            # clipboard_set (pyperclip) expects unicode\n            obj.to_csv(buf,\
    \ sep=sep, encoding=\"utf-8\", **kwargs)\n            text = buf.getvalue()\n\n\
    \            clipboard_set(text)\n            return\n        except TypeError:\n\
    \            warnings.warn(\n                \"to_clipboard in excel mode requires\
    \ a single character separator.\",\n                stacklevel=find_stack_level(),\n\
    \            )\n    elif sep is not None:\n        warnings.warn(\n          \
    \  \"to_clipboard with excel=False ignores the sep argument.\",\n            stacklevel=find_stack_level(),\n\
    \        )\n\n    if isinstance(obj, ABCDataFrame):\n        # str(df) has various\
    \ unhelpful defaults, like truncation\n        with option_context(\"display.max_colwidth\"\
    , None):\n            objstr = obj.to_string(**kwargs)\n    else:\n        objstr\
    \ = str(obj)\n    clipboard_set(objstr)"
- source_sentence: Return a sorted copy of the index.
  sentences:
  - "def sort_values(\n        self,\n        *,\n        return_indexer: bool = False,\n\
    \        ascending: bool = True,\n        na_position: NaPosition = \"last\",\n\
    \        key: Callable | None = None,\n    ) -> Self | tuple[Self, np.ndarray]:\n\
    \        \"\"\"\n        Return a sorted copy of the index.\n\n        Return\
    \ a sorted copy of the index, and optionally return the indices\n        that\
    \ sorted the index itself.\n\n        Parameters\n        ----------\n       \
    \ return_indexer : bool, default False\n            Should the indices that would\
    \ sort the index be returned.\n        ascending : bool, default True\n      \
    \      Should the index values be sorted in an ascending order.\n        na_position\
    \ : {'first' or 'last'}, default 'last'\n            Argument 'first' puts NaNs\
    \ at the beginning, 'last' puts NaNs at\n            the end.\n        key : callable,\
    \ optional\n            If not None, apply the key function to the index values\n\
    \            before sorting. This is similar to the `key` argument in the\n  \
    \          builtin :meth:`sorted` function, with the notable difference that\n\
    \            this `key` function should be *vectorized*. It should expect an\n\
    \            ``Index`` and return an ``Index`` of the same shape.\n\n        Returns\n\
    \        -------\n        sorted_index : pandas.Index\n            Sorted copy\
    \ of the index.\n        indexer : numpy.ndarray, optional\n            The indices\
    \ that the index itself was sorted by.\n\n        See Also\n        --------\n\
    \        Series.sort_values : Sort values of a Series.\n        DataFrame.sort_values\
    \ : Sort values in a DataFrame.\n\n        Examples\n        --------\n      \
    \  >>> idx = pd.Index([10, 100, 1, 1000])\n        >>> idx\n        Index([10,\
    \ 100, 1, 1000], dtype='int64')\n\n        Sort values in ascending order (default\
    \ behavior).\n\n        >>> idx.sort_values()\n        Index([1, 10, 100, 1000],\
    \ dtype='int64')\n\n        Sort values in descending order, and also get the\
    \ indices `idx` was\n        sorted by.\n\n        >>> idx.sort_values(ascending=False,\
    \ return_indexer=True)\n        (Index([1000, 100, 10, 1], dtype='int64'), array([3,\
    \ 1, 0, 2]))\n        \"\"\"\n        if key is None and (\n            (ascending\
    \ and self.is_monotonic_increasing)\n            or (not ascending and self.is_monotonic_decreasing)\n\
    \        ):\n            if return_indexer:\n                indexer = np.arange(len(self),\
    \ dtype=np.intp)\n                return self.copy(), indexer\n            else:\n\
    \                return self.copy()\n\n        # GH 35584. Sort missing values\
    \ according to na_position kwarg\n        # ignore na_position for MultiIndex\n\
    \        if not isinstance(self, ABCMultiIndex):\n            _as = nargsort(\n\
    \                items=self, ascending=ascending, na_position=na_position, key=key\n\
    \            )\n        else:\n            idx = cast(\"Index\", ensure_key_mapped(self,\
    \ key))\n            _as = idx.argsort(na_position=na_position)\n            if\
    \ not ascending:\n                _as = _as[::-1]\n\n        sorted_index = self.take(_as)\n\
    \n        if return_indexer:\n            return sorted_index, _as  # pyright:\
    \ ignore[reportReturnType]\n        else:\n            return sorted_index"
  - "def describe(\n        self,\n        percentiles=None,\n        include=None,\n\
    \        exclude=None,\n    ) -> DataFrame:\n        \"\"\"\n        Generate\
    \ descriptive statistics for each group.\n\n        Within each group, summarize\
    \ the central tendency, dispersion,\n        and shape of each analyzed column's\
    \ distribution, excluding\n        ``NaN`` values. By default only numeric columns\
    \ are analyzed;\n        pass ``include`` to also analyze non-numeric columns\
    \ (or\n        ``exclude`` to omit columns by dtype).\n\n        Parameters\n\
    \        ----------\n        percentiles : list-like of numbers, optional\n  \
    \          The percentiles to include in the output. All should fall\n       \
    \     between 0 and 1. The default, ``None``, returns the 25th,\n            50th,\
    \ and 75th percentiles.\n        include : 'all', list-like of dtypes or None\
    \ (default), optional\n            Which column dtypes to include. Options:\n\n\
    \            - ``'all'`` : Include all columns, including non-numeric ones.\n\
    \            - list-like of dtypes : Limit the result to columns of the\n    \
    \          given dtypes, in the style of\n              :meth:`DataFrame.select_dtypes`\
    \ (e.g. ``include=[np.number]``\n              or ``include=[\"category\"]``).\n\
    \            - ``None`` (default) : Include only numeric columns, falling\n  \
    \            back to object and categorical columns if there are no\n        \
    \      numeric columns.\n        exclude : list-like of dtypes or None (default),\
    \ optional\n            Column dtypes to omit from the result, in the style of\n\
    \            :meth:`DataFrame.select_dtypes`. ``None`` (default) excludes\n  \
    \          nothing.\n\n        Returns\n        -------\n        DataFrame\n \
    \           One row per group. The columns form a MultiIndex whose\n         \
    \   outer level is the analyzed column and whose inner level is\n            the\
    \ statistic name.\n\n        See Also\n        --------\n        DataFrame.describe\
    \ : Generate descriptive statistics of a DataFrame.\n        SeriesGroupBy.describe\
    \ : Generate descriptive statistics for each\n            group of a Series.\n\
    \        DataFrame.select_dtypes : Subset of a DataFrame including/excluding\n\
    \            columns based on their dtype.\n\n        Notes\n        -----\n \
    \       For numeric columns, the per-group statistics are ``count``,\n       \
    \ ``mean``, ``std``, ``min``, ``max``, and the requested\n        percentiles.\
    \ By default the lower percentile is ``25`` and the\n        upper is ``75``;\
    \ the ``50`` percentile is the same as the median.\n\n        For object columns,\
    \ the per-group statistics are ``count``,\n        ``unique``, ``top``, and ``freq``.\
    \ The ``top`` is the most common\n        value within the group and ``freq``\
    \ is its count.\n\n        Examples\n        --------\n        >>> df = pd.DataFrame({\"\
    group\": [\"a\", \"a\", \"b\", \"b\"], \"value\": [1, 2, 3, 4]})\n        >>>\
    \ df.groupby(\"group\").describe()\n              value\n              count mean\
    \       std  min   25%  50%   75%  max\n        group\n        a       2.0  1.5\
    \  0.707107  1.0  1.25  1.5  1.75  2.0\n        b       2.0  3.5  0.707107  3.0\
    \  3.25  3.5  3.75  4.0\n        \"\"\"\n        return super().describe(\n  \
    \          percentiles=percentiles, include=include, exclude=exclude\n       \
    \ )"
  - "def sort_values(\n        self,\n        *,\n        axis: Axis = 0,\n      \
    \  ascending: bool | Sequence[bool] = True,\n        inplace: bool = False,\n\
    \        kind: SortKind = \"quicksort\",\n        na_position: NaPosition = \"\
    last\",\n        ignore_index: bool = False,\n        key: ValueKeyFunc | None\
    \ = None,\n    ) -> Series | None:\n        \"\"\"\n        Sort by the values.\n\
    \n        Sort a Series in ascending or descending order by some\n        criterion.\n\
    \n        Parameters\n        ----------\n        axis : {0 or 'index'}\n    \
    \        Unused. Parameter needed for compatibility with DataFrame.\n        ascending\
    \ : bool or list of bools, default True\n            If True, sort values in ascending\
    \ order, otherwise descending.\n        inplace : bool, default False\n      \
    \      If True, perform operation in-place.\n        kind : {'quicksort', 'mergesort',\
    \ 'heapsort', 'stable'}, default 'quicksort'\n            Choice of sorting algorithm.\
    \ See also :func:`numpy.sort` for more\n            information. 'mergesort' and\
    \ 'stable' are the only stable  algorithms.\n        na_position : {'first' or\
    \ 'last'}, default 'last'\n            Argument 'first' puts NaNs at the beginning,\
    \ 'last' puts NaNs at\n            the end.\n        ignore_index : bool, default\
    \ False\n            If True, the resulting axis will be labeled 0, 1, …, n -\
    \ 1.\n        key : callable, optional\n            If not None, apply the key\
    \ function to the series values\n            before sorting. This is similar to\
    \ the `key` argument in the\n            builtin :meth:`sorted` function, with\
    \ the notable difference that\n            this `key` function should be *vectorized*.\
    \ It should expect a\n            ``Series`` and return an array-like.\n\n   \
    \     Returns\n        -------\n        Series or None\n            Series ordered\
    \ by values or None if ``inplace=True``.\n\n        See Also\n        --------\n\
    \        Series.sort_index : Sort by the Series indices.\n        DataFrame.sort_values\
    \ : Sort DataFrame by the values along either axis.\n        DataFrame.sort_index\
    \ : Sort DataFrame by indices.\n\n        Examples\n        --------\n       \
    \ >>> s = pd.Series([np.nan, 1, 3, 10, 5])\n        >>> s\n        0     NaN\n\
    \        1     1.0\n        2     3.0\n        3     10.0\n        4     5.0\n\
    \        dtype: float64\n\n        Sort values ascending order (default behavior)\n\
    \n        >>> s.sort_values(ascending=True)\n        1     1.0\n        2    \
    \ 3.0\n        4     5.0\n        3    10.0\n        0     NaN\n        dtype:\
    \ float64\n\n        Sort values descending order\n\n        >>> s.sort_values(ascending=False)\n\
    \        3    10.0\n        4     5.0\n        2     3.0\n        1     1.0\n\
    \        0     NaN\n        dtype: float64\n\n        Sort values putting NAs\
    \ first\n\n        >>> s.sort_values(na_position=\"first\")\n        0     NaN\n\
    \        1     1.0\n        2     3.0\n        4     5.0\n        3    10.0\n\
    \        dtype: float64\n\n        Sort a series of strings\n\n        >>> s =\
    \ pd.Series([\"z\", \"b\", \"d\", \"a\", \"c\"])\n        >>> s\n        0   \
    \ z\n        1    b\n        2    d\n        3    a\n        4    c\n        dtype:\
    \ str\n\n        >>> s.sort_values()\n        3    a\n        1    b\n       \
    \ 4    c\n        2    d\n        0    z\n        dtype: str\n\n        Sort using\
    \ a key function. Your `key` function will be\n        given the ``Series`` of\
    \ values and should return an array-like.\n\n        >>> s = pd.Series([\"a\"\
    , \"B\", \"c\", \"D\", \"e\"])\n        >>> s.sort_values()\n        1    B\n\
    \        3    D\n        0    a\n        2    c\n        4    e\n        dtype:\
    \ str\n        >>> s.sort_values(key=lambda x: x.str.lower())\n        0    a\n\
    \        1    B\n        2    c\n        3    D\n        4    e\n        dtype:\
    \ str\n\n        NumPy ufuncs work well here. For example, we can\n        sort\
    \ by the ``sin`` of the value\n\n        >>> s = pd.Series([-4, -2, 0, 2, 4])\n\
    \        >>> s.sort_values(key=np.sin)\n        1   -2\n        4    4\n     \
    \   2    0\n        0   -4\n        3    2\n        dtype: int64\n\n        More\
    \ complicated user-defined functions can be used,\n        as long as they expect\
    \ a Series and return an array-like\n\n        >>> s.sort_values(key=lambda x:\
    \ np.tan(x.cumsum()))\n        0   -4\n        3    2\n        4    4\n      \
    \  1   -2\n        2    0\n        dtype: int64\n        \"\"\"\n        inplace\
    \ = validate_bool_kwarg(inplace, \"inplace\")\n        # Validate the axis parameter\n\
    \        self._get_axis_number(axis)\n\n        if is_list_like(ascending):\n\
    \            ascending = cast(\"Sequence[bool]\", ascending)\n            if len(ascending)\
    \ != 1:\n                raise ValueError(\n                    f\"Length of ascending\
    \ ({len(ascending)}) must be 1 for Series\"\n                )\n            ascending\
    \ = ascending[0]\n\n        ascending = validate_ascending(ascending)\n\n    \
    \    if na_position not in [\"first\", \"last\"]:\n            raise ValueError(f\"\
    invalid na_position: {na_position}\")\n\n        # GH 35922. Make sorting stable\
    \ by leveraging nargsort\n        if key:\n            values_to_sort = cast(\"\
    Series\", ensure_key_mapped(self, key))._values\n        else:\n            values_to_sort\
    \ = self._values\n        sorted_index = nargsort(values_to_sort, kind, bool(ascending),\
    \ na_position)\n\n        if is_range_indexer(sorted_index, len(sorted_index)):\n\
    \            if inplace:\n                return self._update_inplace(self)\n\
    \            return self.copy(deep=False)\n\n        result = self._constructor(\n\
    \            self._values[sorted_index], index=self.index[sorted_index], copy=False\n\
    \        )\n\n        if ignore_index:\n            result.index = default_index(len(sorted_index))\n\
    \n        if not inplace:\n            return result.__finalize__(self, method=\"\
    sort_values\")\n        self._update_inplace(result)\n        return None"
- source_sentence: Test whether file exists.
  sentences:
  - "def file_exists(filepath_or_buffer: FilePath | BaseBuffer) -> bool:\n    \"\"\
    \"Test whether file exists.\"\"\"\n    exists = False\n    filepath_or_buffer\
    \ = stringify_path(filepath_or_buffer)\n    if not isinstance(filepath_or_buffer,\
    \ str):\n        return exists\n    try:\n        exists = os.path.exists(filepath_or_buffer)\n\
    \        # gh-5874: if the filepath is too long will raise here\n    except (TypeError,\
    \ ValueError):\n        pass\n    return exists"
  - "def stringify_path(\n    filepath_or_buffer: FilePath | BaseBufferT,\n    convert_file_like:\
    \ bool = False,\n) -> str | BaseBufferT:\n    \"\"\"\n    Attempt to convert a\
    \ path-like object to a string.\n\n    Parameters\n    ----------\n    filepath_or_buffer\
    \ : object to be converted\n\n    Returns\n    -------\n    str_filepath_or_buffer\
    \ : maybe a string version of the object\n\n    Notes\n    -----\n    Objects\
    \ supporting the fspath protocol are coerced\n    according to its __fspath__\
    \ method.\n\n    Any other object is passed through unchanged, which includes\
    \ bytes,\n    strings, buffers, or anything else that's not even path-like.\n\
    \    \"\"\"\n    if not convert_file_like and is_file_like(filepath_or_buffer):\n\
    \        # GH 38125: some fsspec objects implement os.PathLike but have already\
    \ opened a\n        # file. This prevents opening the file a second time. infer_compression\
    \ calls\n        # this function with convert_file_like=True to infer the compression.\n\
    \        return cast(\"BaseBufferT\", filepath_or_buffer)\n\n    if isinstance(filepath_or_buffer,\
    \ os.PathLike):\n        filepath_or_buffer = filepath_or_buffer.__fspath__()\n\
    \    return _expand_user(filepath_or_buffer)"
  - "def infer_dtype_from_object(dtype) -> type:\n    \"\"\"\n    Get a numpy dtype.type-style\
    \ object for a dtype object.\n\n    This method also includes handling of the\
    \ datetime64[ns] and\n    datetime64[ns, TZ] objects.\n\n    If no dtype can be\
    \ found, we return ``object``.\n\n    Parameters\n    ----------\n    dtype :\
    \ dtype, type\n        The dtype object whose numpy dtype.type-style\n       \
    \ object we want to extract.\n\n    Returns\n    -------\n    type\n    \"\"\"\
    \n    if isinstance(dtype, type) and issubclass(dtype, np.generic):\n        #\
    \ Type object from a dtype\n\n        return dtype\n    elif isinstance(dtype,\
    \ (np.dtype, ExtensionDtype)):\n        # dtype object\n        try:\n       \
    \     _validate_date_like_dtype(dtype)\n        except TypeError:\n          \
    \  # Should still pass if we don't have a date-like\n            pass\n      \
    \  if hasattr(dtype, \"numpy_dtype\"):\n            # TODO: Implement this properly\n\
    \            # https://github.com/pandas-dev/pandas/issues/52576\n           \
    \ return dtype.numpy_dtype.type\n        return dtype.type\n\n    try:\n     \
    \   dtype = pandas_dtype(dtype)\n    except TypeError:\n        pass\n\n    if\
    \ isinstance(dtype, ExtensionDtype):\n        return dtype.type\n    elif isinstance(dtype,\
    \ str):\n        # TODO(jreback)\n        # should deprecate these\n        if\
    \ dtype in [\"datetimetz\", \"datetime64tz\"]:\n            return DatetimeTZDtype.type\n\
    \        elif dtype in [\"period\"]:\n            raise NotImplementedError\n\n\
    \        if dtype in [\"datetime\", \"timedelta\"]:\n            dtype += \"64\"\
    \n        try:\n            return infer_dtype_from_object(getattr(np, dtype))\n\
    \        except (AttributeError, TypeError):\n            # Handles cases like\
    \ _get_dtype(int) i.e.,\n            # Python objects that are valid dtypes\n\
    \            # (unlike user-defined types, in general)\n            #\n      \
    \      # TypeError handles the float16 type code of 'e'\n            # further\
    \ handle internal types\n            pass\n\n    return infer_dtype_from_object(np.dtype(dtype))"
- source_sentence: set my pandas type
  sentences:
  - "def set_attrs(self) -> None:\n        \"\"\"set our table type & indexables\"\
    \"\"\n        self.attrs.table_type = str(self.table_type)\n        self.attrs.index_cols\
    \ = self.index_cols()\n        self.attrs.values_cols = self.values_cols()\n \
    \       self.attrs.non_index_axes = self.non_index_axes\n        self.attrs.data_columns\
    \ = self.data_columns\n        self.attrs.nan_rep = self.nan_rep\n        self.attrs.encoding\
    \ = self.encoding\n        self.attrs.errors = self.errors\n        self.attrs.levels\
    \ = self.levels\n        self.attrs.info = self.info"
  - "def set_object_info(self) -> None:\n        \"\"\"set my pandas type\"\"\"\n\
    \        self.attrs.pandas_type = str(self.pandas_kind)"
  - "def isin(self, values, level=None) -> npt.NDArray[np.bool_]:\n        \"\"\"\n\
    \        Return a boolean array where the index values are in `values`.\n\n  \
    \      Compute boolean array of whether each index value is found in the\n   \
    \     passed set of values. The length of the returned boolean array matches\n\
    \        the length of the index.\n\n        Parameters\n        ----------\n\
    \        values : set or list-like\n            Sought values.\n        level\
    \ : str or int, optional\n            Name or position of the index level to use\
    \ (if the index is a\n            `MultiIndex`).\n\n        Returns\n        -------\n\
    \        np.ndarray[bool]\n            NumPy array of boolean values.\n\n    \
    \    See Also\n        --------\n        Series.isin : Same for Series.\n    \
    \    DataFrame.isin : Same method for DataFrames.\n\n        Notes\n        -----\n\
    \        In the case of `MultiIndex` you must either specify `values` as a\n \
    \       list-like object containing tuples that are the same length as the\n \
    \       number of levels, or specify `level`. Otherwise it will raise a\n    \
    \    ``ValueError``.\n\n        If `level` is specified:\n\n        - if it is\
    \ the name of one *and only one* index level, use that level;\n        - otherwise\
    \ it should be a number indicating level position.\n\n        Examples\n     \
    \   --------\n        >>> idx = pd.Index([1, 2, 3])\n        >>> idx\n       \
    \ Index([1, 2, 3], dtype='int64')\n\n        Check whether each index value in\
    \ a list of values.\n\n        >>> idx.isin([1, 4])\n        array([ True, False,\
    \ False])\n\n        >>> mi = pd.MultiIndex.from_arrays(\n        ...     [[1,\
    \ 2, 3], [\"red\", \"blue\", \"green\"]], names=[\"number\", \"color\"]\n    \
    \    ... )\n        >>> mi\n        MultiIndex([(1,   'red'),\n              \
    \      (2,  'blue'),\n                    (3, 'green')],\n                   names=['number',\
    \ 'color'])\n\n        Check whether the strings in the 'color' level of the MultiIndex\n\
    \        are in a list of colors.\n\n        >>> mi.isin([\"red\", \"orange\"\
    , \"yellow\"], level=\"color\")\n        array([ True, False, False])\n\n    \
    \    To check across the levels of a MultiIndex, pass a list of tuples:\n\n  \
    \      >>> mi.isin([(1, \"red\"), (3, \"red\")])\n        array([ True, False,\
    \ False])\n        \"\"\"\n        if isinstance(values, Generator):\n       \
    \     values = list(values)\n\n        if level is None:\n            if len(values)\
    \ == 0:\n                return np.zeros((len(self),), dtype=np.bool_)\n     \
    \       if not isinstance(values, MultiIndex):\n                values = MultiIndex.from_tuples(values)\n\
    \            return values.unique().get_indexer_for(self) != -1\n        else:\n\
    \            num = self._get_level_number(level)\n            levs = self.get_level_values(num)\n\
    \n            if levs.size == 0:\n                return np.zeros(len(levs), dtype=np.bool_)\n\
    \            return levs.isin(values)"
- source_sentence: Write a DataFrame to the Optimized Row Columnar (ORC) format.
  sentences:
  - "def cov(\n        self,\n        other: Series,\n        min_periods: int | None\
    \ = None,\n        ddof: int | None = 1,\n    ) -> float:\n        \"\"\"\n  \
    \      Compute covariance with Series, excluding missing values.\n\n        The\
    \ two `Series` objects are not required to be the same length and\n        will\
    \ be aligned internally before the covariance is calculated.\n\n        Parameters\n\
    \        ----------\n        other : Series\n            Series with which to\
    \ compute the covariance.\n        min_periods : int, optional\n            Minimum\
    \ number of observations needed to have a valid result.\n        ddof : int, default\
    \ 1\n            Delta degrees of freedom.  The divisor used in calculations\n\
    \            is ``N - ddof``, where ``N`` represents the number of elements.\n\
    \n        Returns\n        -------\n        float\n            Covariance between\
    \ Series and other normalized by N-1\n            (unbiased estimator).\n\n  \
    \      See Also\n        --------\n        DataFrame.cov : Compute pairwise covariance\
    \ of columns.\n\n        Examples\n        --------\n        >>> s1 = pd.Series([0.90010907,\
    \ 0.13484424, 0.62036035])\n        >>> s2 = pd.Series([0.12528585, 0.26962463,\
    \ 0.51111198])\n        >>> s1.cov(s2)\n        -0.01685762652715874\n       \
    \ \"\"\"\n        this, other = self.align(other, join=\"inner\")\n        if\
    \ len(this) == 0:\n            return np.nan\n        this_values = this.to_numpy(dtype=float,\
    \ na_value=np.nan, copy=False)\n        other_values = other.to_numpy(dtype=float,\
    \ na_value=np.nan, copy=False)\n        result = nanops.nancov(\n            this_values,\
    \ other_values, min_periods=min_periods, ddof=ddof\n        )\n        result\
    \ = maybe_unbox_numpy_scalar(result)\n        return result"
  - "def to_orc(\n    df: DataFrame,\n    path: FilePath | WriteBuffer[bytes] | None\
    \ = None,\n    *,\n    engine: Literal[\"pyarrow\"] = \"pyarrow\",\n    index:\
    \ bool | None = None,\n    engine_kwargs: dict[str, Any] | None = None,\n) ->\
    \ bytes | None:\n    \"\"\"\n    Write a DataFrame to the ORC format.\n\n    Parameters\n\
    \    ----------\n    df : DataFrame\n        The dataframe to be written to ORC.\
    \ Raises NotImplementedError\n        if dtype of one or more columns is category,\
    \ unsigned integers,\n        intervals, periods or sparse.\n    path : str, file-like\
    \ object or None, default None\n        If a string, it will be used as the root\
    \ directory path\n        when writing a partitioned dataset. By file-like object,\n\
    \        we refer to objects with a write() method, such as a file handle\n  \
    \      (e.g. via builtin open function). If path is None,\n        a bytes object\
    \ is returned.\n\n        The string could be a URL. Valid URL schemes include\
    \ http, ftp, s3,\n        gs, and file. For file URLs, a host is expected. A local\
    \ file could be:\n        ``file://localhost/path/to/table.orc``. A remote example\
    \ could be:\n        ``s3://bucket/path/to/table.orc``.\n\n        Certain URL\
    \ schemes may require additional packages. For example, S3\n        URLs require\
    \ the ``s3fs`` library. See\n        :ref:`install.optional_dependencies` for\
    \ a full list.\n    engine : str, default 'pyarrow'\n        ORC library to use.\n\
    \    index : bool, optional\n        If ``True``, include the dataframe's index(es)\
    \ in the file output. If\n        ``False``, they will not be written to the file.\n\
    \        If ``None``, similar to ``infer`` the dataframe's index(es)\n       \
    \ will be saved. However, instead of being saved as values,\n        the RangeIndex\
    \ will be stored as a range in the metadata so it\n        doesn't require much\
    \ space and is faster. Other indexes will\n        be included as columns in the\
    \ file output.\n    engine_kwargs : dict[str, Any] or None, default None\n   \
    \     Additional keyword arguments passed to :func:`pyarrow.orc.write_table`.\n\
    \n    Returns\n    -------\n    bytes if no path argument is provided else None\n\
    \n    Raises\n    ------\n    NotImplementedError\n        Dtype of one or more\
    \ columns is category, unsigned integers, interval,\n        period or sparse.\n\
    \    ValueError\n        engine is not pyarrow.\n\n    Notes\n    -----\n    *\
    \ Before using this function you should read the\n      :ref:`user guide about\
    \ ORC <io.orc>` and\n      :ref:`install optional dependencies <install.warn_orc>`.\n\
    \    * This function requires `pyarrow <https://arrow.apache.org/docs/python/>`_\n\
    \      library.\n    * For supported dtypes please refer to `supported ORC features\
    \ in Arrow\n      <https://arrow.apache.org/docs/cpp/orc.html#data-types>`__.\n\
    \    * Currently timezones in datetime columns are not preserved when a\n    \
    \  dataframe is converted into ORC files.\n    \"\"\"\n    if index is None:\n\
    \        index = df.index.names[0] is not None\n    if engine_kwargs is None:\n\
    \        engine_kwargs = {}\n\n    # validate index\n    # --------------\n\n\
    \    # validate that we have only a default index\n    # raise on anything else\
    \ as we don't serialize the index\n\n    if not df.index.equals(default_index(len(df))):\n\
    \        raise ValueError(\n            \"orc does not support serializing a non-default\
    \ index for the index; \"\n            \"you can .reset_index() to make the index\
    \ into column(s)\"\n        )\n\n    if df.index.name is not None:\n        raise\
    \ ValueError(\"orc does not serialize index meta-data on a default index\")\n\n\
    \    if engine != \"pyarrow\":\n        raise ValueError(\"engine must be 'pyarrow'\"\
    )\n    pa = import_optional_dependency(\"pyarrow\")\n    orc = import_optional_dependency(\"\
    pyarrow.orc\")\n\n    was_none = path is None\n    if was_none:\n        path\
    \ = io.BytesIO()\n    assert path is not None  # For mypy\n    with get_handle(path,\
    \ \"wb\", is_text=False) as handles:\n        try:\n            orc.write_table(\n\
    \                pa.Table.from_pandas(df, preserve_index=index),\n           \
    \     handles.handle,\n                **engine_kwargs,\n            )\n     \
    \   except (TypeError, pa.ArrowNotImplementedError) as e:\n            raise NotImplementedError(\n\
    \                \"The dtype of one or more columns is not supported yet.\"\n\
    \            ) from e\n\n    if was_none:\n        assert isinstance(path, io.BytesIO)\
    \  # For mypy\n        return path.getvalue()\n    return None"
  - "def to_orc(\n        self,\n        path: FilePath | WriteBuffer[bytes] | None\
    \ = None,\n        *,\n        engine: Literal[\"pyarrow\"] = \"pyarrow\",\n \
    \       index: bool | None = None,\n        engine_kwargs: dict[str, Any] | None\
    \ = None,\n    ) -> bytes | None:\n        \"\"\"\n        Write a DataFrame to\
    \ the Optimized Row Columnar (ORC) format.\n\n        ORC is a self-describing,\
    \ type-aware columnar file format designed\n        for Hadoop workloads. It provides\
    \ efficient compression and encoding\n        schemes, making it well-suited for\
    \ large-scale data storage and\n        analytics. This method requires the ``pyarrow``\
    \ library.\n\n        Parameters\n        ----------\n        path : str, file-like\
    \ object or None, default None\n            If a string, it will be used as the\
    \ root directory path\n            when writing a partitioned dataset. By file-like\
    \ object,\n            we refer to objects with a write() method, such as a file\
    \ handle\n            (e.g. via builtin open function). If path is None,\n   \
    \         a bytes object is returned.\n\n            The string could be a URL.\
    \ Valid URL schemes include http, ftp, s3,\n            gs, and file. For file\
    \ URLs, a host is expected. A local file could be:\n            ``file://localhost/path/to/table.orc``.\
    \ A remote example could be:\n            ``s3://bucket/path/to/table.orc``.\n\
    \n            Certain URL schemes may require additional packages. For example,\
    \ S3\n            URLs require the ``s3fs`` library. See\n            :ref:`install.optional_dependencies`\
    \ for a full list.\n        engine : {'pyarrow'}, default 'pyarrow'\n        \
    \    ORC library to use.\n        index : bool, optional\n            If ``True``,\
    \ include the dataframe's index(es) in the file output.\n            If ``False``,\
    \ they will not be written to the file.\n            If ``None``, similar to ``infer``\
    \ the dataframe's index(es)\n            will be saved. However, instead of being\
    \ saved as values,\n            the RangeIndex will be stored as a range in the\
    \ metadata so it\n            doesn't require much space and is faster. Other\
    \ indexes will\n            be included as columns in the file output.\n     \
    \   engine_kwargs : dict[str, Any] or None, default None\n            Additional\
    \ keyword arguments passed to :func:`pyarrow.orc.write_table`.\n\n        Returns\n\
    \        -------\n        bytes if no ``path`` argument is provided else None\n\
    \            Bytes object with DataFrame data if ``path`` is not specified else\
    \ None.\n\n        Raises\n        ------\n        NotImplementedError\n     \
    \       Dtype of one or more columns is category, unsigned integers, interval,\n\
    \            period or sparse.\n        ValueError\n            engine is not\
    \ pyarrow.\n\n        See Also\n        --------\n        read_orc : Read a ORC\
    \ file.\n        DataFrame.to_parquet : Write a parquet file.\n        DataFrame.to_csv\
    \ : Write a csv file.\n        DataFrame.to_sql : Write to a sql table.\n    \
    \    DataFrame.to_hdf : Write to hdf.\n\n        Notes\n        -----\n      \
    \  * Find more information on ORC\n          `here <https://en.wikipedia.org/wiki/Apache_ORC>`__.\n\
    \        * Before using this function you should read the :ref:`user guide about\n\
    \          ORC <io.orc>` and :ref:`install optional dependencies <install.warn_orc>`.\n\
    \        * This function requires `pyarrow <https://arrow.apache.org/docs/python/>`_\n\
    \          library.\n        * For supported dtypes please refer to `supported\
    \ ORC features in Arrow\n          <https://arrow.apache.org/docs/cpp/orc.html#data-types>`__.\n\
    \        * Currently timezones in datetime columns are not preserved when a\n\
    \          dataframe is converted into ORC files.\n\n        Examples\n      \
    \  --------\n        >>> df = pd.DataFrame(data={\"col1\": [1, 2], \"col2\": [4,\
    \ 3]})\n        >>> df.to_orc(\"df.orc\")  # doctest: +SKIP\n        >>> pd.read_orc(\"\
    df.orc\")  # doctest: +SKIP\n           col1  col2\n        0     1     4\n  \
    \      1     2     3\n\n        If you want to get a buffer to the orc content\
    \ you can write it to io.BytesIO\n\n        >>> import io\n        >>> b = io.BytesIO(df.to_orc())\
    \  # doctest: +SKIP\n        >>> b.seek(0)  # doctest: +SKIP\n        0\n    \
    \    >>> content = b.read()  # doctest: +SKIP\n        \"\"\"\n        from pandas.io.orc\
    \ import to_orc\n\n        return to_orc(\n            self, path, engine=engine,\
    \ index=index, engine_kwargs=engine_kwargs\n        )"
pipeline_tag: sentence-similarity
library_name: sentence-transformers
metrics:
- cosine_accuracy
model-index:
- name: SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: triplet
      name: Triplet
    dataset:
      name: pandas val
      type: pandas-val
    metrics:
    - type: cosine_accuracy
      value: 1.0
      name: Cosine Accuracy
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'BertModel'})
  (1): Pooling({'embedding_dimension': 384, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```
Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Write a DataFrame to the Optimized Row Columnar (ORC) format.',
    'def to_orc(\n        self,\n        path: FilePath | WriteBuffer[bytes] | None = None,\n        *,\n        engine: Literal["pyarrow"] = "pyarrow",\n        index: bool | None = None,\n        engine_kwargs: dict[str, Any] | None = None,\n    ) -> bytes | None:\n        """\n        Write a DataFrame to the Optimized Row Columnar (ORC) format.\n\n        ORC is a self-describing, type-aware columnar file format designed\n        for Hadoop workloads. It provides efficient compression and encoding\n        schemes, making it well-suited for large-scale data storage and\n        analytics. This method requires the ``pyarrow`` library.\n\n        Parameters\n        ----------\n        path : str, file-like object or None, default None\n            If a string, it will be used as the root directory path\n            when writing a partitioned dataset. By file-like object,\n            we refer to objects with a write() method, such as a file handle\n            (e.g. via builtin open function). If path is None,\n            a bytes object is returned.\n\n            The string could be a URL. Valid URL schemes include http, ftp, s3,\n            gs, and file. For file URLs, a host is expected. A local file could be:\n            ``file://localhost/path/to/table.orc``. A remote example could be:\n            ``s3://bucket/path/to/table.orc``.\n\n            Certain URL schemes may require additional packages. For example, S3\n            URLs require the ``s3fs`` library. See\n            :ref:`install.optional_dependencies` for a full list.\n        engine : {\'pyarrow\'}, default \'pyarrow\'\n            ORC library to use.\n        index : bool, optional\n            If ``True``, include the dataframe\'s index(es) in the file output.\n            If ``False``, they will not be written to the file.\n            If ``None``, similar to ``infer`` the dataframe\'s index(es)\n            will be saved. However, instead of being saved as values,\n            the RangeIndex will be stored as a range in the metadata so it\n            doesn\'t require much space and is faster. Other indexes will\n            be included as columns in the file output.\n        engine_kwargs : dict[str, Any] or None, default None\n            Additional keyword arguments passed to :func:`pyarrow.orc.write_table`.\n\n        Returns\n        -------\n        bytes if no ``path`` argument is provided else None\n            Bytes object with DataFrame data if ``path`` is not specified else None.\n\n        Raises\n        ------\n        NotImplementedError\n            Dtype of one or more columns is category, unsigned integers, interval,\n            period or sparse.\n        ValueError\n            engine is not pyarrow.\n\n        See Also\n        --------\n        read_orc : Read a ORC file.\n        DataFrame.to_parquet : Write a parquet file.\n        DataFrame.to_csv : Write a csv file.\n        DataFrame.to_sql : Write to a sql table.\n        DataFrame.to_hdf : Write to hdf.\n\n        Notes\n        -----\n        * Find more information on ORC\n          `here <https://en.wikipedia.org/wiki/Apache_ORC>`__.\n        * Before using this function you should read the :ref:`user guide about\n          ORC <io.orc>` and :ref:`install optional dependencies <install.warn_orc>`.\n        * This function requires `pyarrow <https://arrow.apache.org/docs/python/>`_\n          library.\n        * For supported dtypes please refer to `supported ORC features in Arrow\n          <https://arrow.apache.org/docs/cpp/orc.html#data-types>`__.\n        * Currently timezones in datetime columns are not preserved when a\n          dataframe is converted into ORC files.\n\n        Examples\n        --------\n        >>> df = pd.DataFrame(data={"col1": [1, 2], "col2": [4, 3]})\n        >>> df.to_orc("df.orc")  # doctest: +SKIP\n        >>> pd.read_orc("df.orc")  # doctest: +SKIP\n           col1  col2\n        0     1     4\n        1     2     3\n\n        If you want to get a buffer to the orc content you can write it to io.BytesIO\n\n        >>> import io\n        >>> b = io.BytesIO(df.to_orc())  # doctest: +SKIP\n        >>> b.seek(0)  # doctest: +SKIP\n        0\n        >>> content = b.read()  # doctest: +SKIP\n        """\n        from pandas.io.orc import to_orc\n\n        return to_orc(\n            self, path, engine=engine, index=index, engine_kwargs=engine_kwargs\n        )',
    'def to_orc(\n    df: DataFrame,\n    path: FilePath | WriteBuffer[bytes] | None = None,\n    *,\n    engine: Literal["pyarrow"] = "pyarrow",\n    index: bool | None = None,\n    engine_kwargs: dict[str, Any] | None = None,\n) -> bytes | None:\n    """\n    Write a DataFrame to the ORC format.\n\n    Parameters\n    ----------\n    df : DataFrame\n        The dataframe to be written to ORC. Raises NotImplementedError\n        if dtype of one or more columns is category, unsigned integers,\n        intervals, periods or sparse.\n    path : str, file-like object or None, default None\n        If a string, it will be used as the root directory path\n        when writing a partitioned dataset. By file-like object,\n        we refer to objects with a write() method, such as a file handle\n        (e.g. via builtin open function). If path is None,\n        a bytes object is returned.\n\n        The string could be a URL. Valid URL schemes include http, ftp, s3,\n        gs, and file. For file URLs, a host is expected. A local file could be:\n        ``file://localhost/path/to/table.orc``. A remote example could be:\n        ``s3://bucket/path/to/table.orc``.\n\n        Certain URL schemes may require additional packages. For example, S3\n        URLs require the ``s3fs`` library. See\n        :ref:`install.optional_dependencies` for a full list.\n    engine : str, default \'pyarrow\'\n        ORC library to use.\n    index : bool, optional\n        If ``True``, include the dataframe\'s index(es) in the file output. If\n        ``False``, they will not be written to the file.\n        If ``None``, similar to ``infer`` the dataframe\'s index(es)\n        will be saved. However, instead of being saved as values,\n        the RangeIndex will be stored as a range in the metadata so it\n        doesn\'t require much space and is faster. Other indexes will\n        be included as columns in the file output.\n    engine_kwargs : dict[str, Any] or None, default None\n        Additional keyword arguments passed to :func:`pyarrow.orc.write_table`.\n\n    Returns\n    -------\n    bytes if no path argument is provided else None\n\n    Raises\n    ------\n    NotImplementedError\n        Dtype of one or more columns is category, unsigned integers, interval,\n        period or sparse.\n    ValueError\n        engine is not pyarrow.\n\n    Notes\n    -----\n    * Before using this function you should read the\n      :ref:`user guide about ORC <io.orc>` and\n      :ref:`install optional dependencies <install.warn_orc>`.\n    * This function requires `pyarrow <https://arrow.apache.org/docs/python/>`_\n      library.\n    * For supported dtypes please refer to `supported ORC features in Arrow\n      <https://arrow.apache.org/docs/cpp/orc.html#data-types>`__.\n    * Currently timezones in datetime columns are not preserved when a\n      dataframe is converted into ORC files.\n    """\n    if index is None:\n        index = df.index.names[0] is not None\n    if engine_kwargs is None:\n        engine_kwargs = {}\n\n    # validate index\n    # --------------\n\n    # validate that we have only a default index\n    # raise on anything else as we don\'t serialize the index\n\n    if not df.index.equals(default_index(len(df))):\n        raise ValueError(\n            "orc does not support serializing a non-default index for the index; "\n            "you can .reset_index() to make the index into column(s)"\n        )\n\n    if df.index.name is not None:\n        raise ValueError("orc does not serialize index meta-data on a default index")\n\n    if engine != "pyarrow":\n        raise ValueError("engine must be \'pyarrow\'")\n    pa = import_optional_dependency("pyarrow")\n    orc = import_optional_dependency("pyarrow.orc")\n\n    was_none = path is None\n    if was_none:\n        path = io.BytesIO()\n    assert path is not None  # For mypy\n    with get_handle(path, "wb", is_text=False) as handles:\n        try:\n            orc.write_table(\n                pa.Table.from_pandas(df, preserve_index=index),\n                handles.handle,\n                **engine_kwargs,\n            )\n        except (TypeError, pa.ArrowNotImplementedError) as e:\n            raise NotImplementedError(\n                "The dtype of one or more columns is not supported yet."\n            ) from e\n\n    if was_none:\n        assert isinstance(path, io.BytesIO)  # For mypy\n        return path.getvalue()\n    return None',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.8506, 0.5592],
#         [0.8506, 1.0000, 0.7586],
#         [0.5592, 0.7586, 1.0000]])
```
<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Triplet

* Dataset: `pandas-val`
* Evaluated with [<code>TripletEvaluator</code>](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html#sentence_transformers.sentence_transformer.evaluation.TripletEvaluator)

| Metric              | Value   |
|:--------------------|:--------|
| **cosine_accuracy** | **1.0** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 2,039 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>sentence_2</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                         | sentence_1                                                                           | sentence_2                                                                           |
  |:---------|:-----------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|
  | type     | string                                                                             | string                                                                               | string                                                                               |
  | modality | text                                                                               | text                                                                                 | text                                                                                 |
  | details  | <ul><li>min: 5 tokens</li><li>mean: 17.21 tokens</li><li>max: 117 tokens</li></ul> | <ul><li>min: 24 tokens</li><li>mean: 200.62 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 31 tokens</li><li>mean: 230.23 tokens</li><li>max: 256 tokens</li></ul> |
* Samples:
  | sentence_0                                                           | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | sentence_2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
  |:---------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>Compute slice locations for input labels.</code>               | <code>def slice_locs(<br>        self,<br>        start: SliceType = None,<br>        end: SliceType = None,<br>        step: int \| None = None,<br>    ) -> tuple[int, int]:<br>        """<br>        Compute slice locations for input labels.<br><br>        This method determines the integer start and end positions for a<br>        label-based slice, which is useful for translating label-based<br>        slicing into positional slicing on the underlying data.<br><br>        Parameters<br>        ----------<br>        start : label, default None<br>            If None, defaults to the beginning.<br>        end : label, default None<br>            If None, defaults to the end.<br>        step : int, defaults None<br>            If None, defaults to 1.<br><br>        Returns<br>        -------<br>        tuple[int, int]<br>            Returns a tuple of two integers representing the slice locations for the<br>            input labels within the index.<br><br>        See Also<br>        --------<br>        Index.get_loc : Get location for a single label.<br>        Index.get_slice_bound ...</code> | <code>def slice_indexer(<br>        self,<br>        start: Hashable \| None = None,<br>        end: Hashable \| None = None,<br>        step: int \| None = None,<br>    ) -> slice:<br>        """<br>        Compute the slice indexer for input labels and step.<br><br>        Index needs to be ordered and unique.<br><br>        Parameters<br>        ----------<br>        start : label, default None<br>            If None, defaults to the beginning.<br>        end : label, default None<br>            If None, defaults to the end.<br>        step : int, default None<br>            If None, defaults to 1.<br><br>        Returns<br>        -------<br>        slice<br>            A slice object.<br><br>        Raises<br>        ------<br>        KeyError : If key does not exist, or key is not unique and index is<br>            not ordered.<br><br>        See Also<br>        --------<br>        Index.slice_locs : Computes slice locations for input labels.<br>        Index.get_slice_bound : Retrieves slice bound that corresponds to given label.<br><br>        Notes<br>        -----<br>        This function assu...</code> |
  | <code>Compute the ExtensionArray of unique values.</code>            | <code>def unique(self) -> Self:<br>        """<br>        Compute the ExtensionArray of unique values.<br><br>        This method returns a new ExtensionArray containing the distinct<br>        values from the original array, preserving the order of first<br>        appearance.<br><br>        Returns<br>        -------<br>        pandas.api.extensions.ExtensionArray<br>            With unique values from the input array.<br><br>        See Also<br>        --------<br>        Index.unique: Return unique values in the index.<br>        Series.unique: Return unique values of Series object.<br>        unique: Return unique values based on a hash table.<br><br>        Examples<br>        --------<br>        >>> arr = pd.array([1, 2, 3, 1, 2, 3])<br>        >>> arr.unique()<br>        <IntegerArray><br>        [1, 2, 3]<br>        Length: 3, dtype: Int64<br>        """<br>        uniques = unique(self.astype(object))<br>        return self._from_sequence(uniques, dtype=self.dtype)</code>                                                                                                                   | <code>def unique(self) -> ArrayLike:<br>        """<br>        Return unique values of Series object.<br><br>        Uniques are returned in order of appearance. Hash table-based unique,<br>        therefore does NOT sort.<br><br>        Returns<br>        -------<br>        ndarray or ExtensionArray<br>            The unique values returned as a NumPy array. See Notes.<br><br>        See Also<br>        --------<br>        Series.drop_duplicates : Return Series with duplicate values removed.<br>        unique : Top-level unique method for any 1-d array-like object.<br>        Index.unique : Return Index with unique values from an Index object.<br><br>        Notes<br>        -----<br>        Returns the unique values as a NumPy array. In case of an<br>        extension-array backed Series, a new<br>        :class:`~api.extensions.ExtensionArray` of that type with just<br>        the unique values is returned. This includes<br><br>            * Categorical<br>            * Period<br>            * Datetime with Timezone<br>            * Datetime without Timezone<br>            ...</code>                            |
  | <code>Return True if hash(obj) will succeed, False otherwise.</code> | <code>def is_hashable(obj: object, allow_slice: bool = True) -> TypeGuard[Hashable]:<br>    """<br>    Return True if hash(obj) will succeed, False otherwise.<br><br>    Some types will pass a test against collections.abc.Hashable but fail when<br>    they are actually hashed with hash().<br><br>    Distinguish between these and other types by trying the call to hash() and<br>    seeing if they raise TypeError.<br><br>    Parameters<br>    ----------<br>    obj : object<br>        The object to check for hashability. Any Python object can be passed here.<br>    allow_slice : bool<br>        If True, return True if the object is hashable (including slices).<br>        If False, return True if the object is hashable and not a slice.<br><br>    Returns<br>    -------<br>    bool<br>        True if object can be hashed (i.e., does not raise TypeError when<br>        passed to hash()) and passes the slice check according to 'allow_slice'.<br>        False otherwise (e.g., if object is mutable like a list or dictionary<br>        or if allow_slice is False and object ...</code>                       | <code>def is_named_tuple(obj: object) -> bool:<br>    """<br>    Check if the object is a named tuple.<br><br>    A named tuple is a subclass of :class:`tuple` that has named fields,<br>    as created by :func:`collections.namedtuple`.<br><br>    Parameters<br>    ----------<br>    obj : object<br>        The object that will be checked to determine<br>        whether it is a named tuple.<br><br>    Returns<br>    -------<br>    bool<br>        Whether `obj` is a named tuple.<br><br>    See Also<br>    --------<br>    api.types.is_dict_like: Check if the object is dict-like.<br>    api.types.is_hashable: Return True if hash(obj)<br>                                  will succeed, False otherwise.<br>    api.types.is_categorical_dtype : Check if the dtype is categorical.<br><br>    Examples<br>    --------<br>    >>> from collections import namedtuple<br>    >>> from pandas.api.types import is_named_tuple<br>    >>> Point = namedtuple("Point", ["x", "y"])<br>    >>> p = Point(1, 2)<br>    >>><br>    >>> is_named_tuple(p)<br>    True<br>    >>> is_named_tuple((1, 2))<br>    False<br>    """<br>    retur...</code>    |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 4
- `per_device_eval_batch_size`: 32
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 4
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 32
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | pandas-val_cosine_accuracy |
|:------:|:----:|:--------------------------:|
| 0.3438 | 22   | 0.9427                     |
| 0.6875 | 44   | 0.9692                     |
| 1.0    | 64   | 0.9824                     |
| 1.0312 | 66   | 0.9824                     |
| 1.375  | 88   | 0.9868                     |
| 1.7188 | 110  | 0.9956                     |
| 2.0    | 128  | 0.9912                     |
| 2.0625 | 132  | 0.9956                     |
| 2.4062 | 154  | 1.0                        |


### Training Time
- **Training**: 1.9 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.5.1
- Transformers: 5.9.0
- PyTorch: 2.11.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->