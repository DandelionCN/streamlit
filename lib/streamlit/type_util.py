# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A bunch of useful utilities for dealing with types."""

# Python 2/3 compatibility
from __future__ import print_function, division, unicode_literals, absolute_import
from streamlit.compatibility import setup_2_3_shims

setup_2_3_shims(globals())

import re


def is_type(obj, fqn_type_pattern):
    """Check type without importing expensive modules.

    Parameters
    ----------
    obj : any
        The object to type-check.
    fqn_type_pattern : str or regex
        The fully-qualified type string or a regular expression.
        Regexes should start with `^` and end with `$`.

    Example
    -------

    To check whether something is a Matplotlib Figure without importing
    matplotlib, use:

    >>> is_type(foo, 'matplotlib.figure.Figure')

    """
    the_type = type(obj)
    module = the_type.__module__
    name = the_type.__name__
    actual_fqn = "%s.%s" % (module, name)
    if isinstance(fqn_type_pattern, string_types):
        return fqn_type_pattern == actual_fqn
    else:
        return fqn_type_pattern.match(actual_fqn) is not None


_SYMPY_RE = re.compile(r"^sympy.*$")


def is_sympy_expession(obj):
    """True if input is a SymPy expression."""
    if not is_type(obj, _SYMPY_RE):
        return False

    try:
        import sympy

        if isinstance(obj, sympy.Expr):
            return True
    except:
        return False


_ALTAIR_RE = re.compile(r"^altair\.vegalite\.v\d+\.api\.\w*Chart$")


def is_altair_chart(obj):
    """True if input looks like an Altair chart."""
    return is_type(obj, _ALTAIR_RE)


def is_keras_model(obj):
    """True if input looks like a Keras model."""
    return (
        is_type(obj, "keras.engine.sequential.Sequential")
        or is_type(obj, "keras.engine.training.Model")
        or is_type(obj, "tensorflow.python.keras.engine.sequential.Sequential")
        or is_type(obj, "tensorflow.python.keras.engine.training.Model")
    )


def is_plotly_chart(obj):
    """True if input looks like a Plotly chart."""
    return (
        is_type(obj, "plotly.graph_objs._figure.Figure")
        or _is_list_of_plotly_objs(obj)
        or _is_probably_plotly_dict(obj)
    )


def is_graphviz_chart(obj):
    """True if input looks like a GraphViz chart."""
    return is_type(obj, "graphviz.dot.Graph") or is_type(obj, "graphviz.dot.Digraph")


def _is_plotly_obj(obj):
    """True if input if from a type that lives in plotly.plotly_objs."""
    the_type = type(obj)
    return the_type.__module__.startswith("plotly.graph_objs")


def _is_list_of_plotly_objs(obj):
    if type(obj) is not list:
        return False
    if len(obj) == 0:
        return False
    return all(_is_plotly_obj(item) for item in obj)


def _is_probably_plotly_dict(obj):
    if type(obj) not in dict_types:
        return False

    if len(obj.keys()) == 0:
        return False

    if any(k not in ["config", "data", "frames", "layout"] for k in obj.keys()):
        return False

    if any(_is_plotly_obj(v) for v in obj.values()):
        return True

    if any(_is_list_of_plotly_objs(v) for v in obj.values()):
        return True

    return False


_FUNCTION_TYPE = type(lambda: 0)


def is_function(x):
    """Return True if x is a function."""
    return type(x) == _FUNCTION_TYPE


def is_namedtuple(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n).__name__ == "str" for n in f)
