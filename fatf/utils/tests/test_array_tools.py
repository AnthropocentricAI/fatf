"""
Tests array tools.
"""
# Author: Kacper Sokol <k.sokol@bristol.ac.uk>
# License: new BSD

import numpy as np

import pytest

import fatf.utils.array_tools as fuat
import fatf.utils.validation as fuv
from fatf.utils.tests.test_validation import (
    BASE_NP_ARRAY, NOT_BASE_NP_ARRAY, NOT_BASE_STRUCTURED_ARRAY,
    NOT_NUMERICAL_NP_ARRAY, NOT_NUMERICAL_STRUCTURED_ARRAY, NUMERICAL_NP_ARRAY,
    NUMERICAL_STRUCTURED_ARRAY, WIDE_NP_ARRAY, WIDE_STRUCTURED_ARRAY)

NUMERICAL_UNSTRUCTURED_ARRAY = np.array([
    [1.0, 1.0 + 1j],
    [1, 1 + 1j],
    [np.nan, -1 + 1j],
    [np.inf, -1 + 1j],
    [-np.inf, -1 + 1j],
    [-1, -1 + 1j]])  # yapf: disable
NOT_NUMERICAL_UNSTRUCTURED_ARRAY = np.array([
    [1 + 0.j, 'a'],
    [1 + 0.j, 'b'],
    [-1 + 0.j, 'c'],
    [1 + 0.j, 'd'],
    [1 + 1j, 'e'],
    [0j, 'f'],
    [np.nan + 0j, 'g'],
    [np.inf + 0j, 'h'],
    [-np.inf + 0j, 'i']])  # yapf: disable
WIDE_UNSTRUCTURED_ARRAY = np.array([
    [1.0, 1.0 + 1j, np.nan],
    [np.inf, 1 + 1j, 6],
    [-1, -1 + 1j, -np.inf]])  # yapf: disable

NP_VER = [int(i) for i in np.version.version.split('.')]


def _compare_nan_arrays(array1, array2):
    """
    Compares 2 numpy arrays and returns True if they are element-wise the same.
    """
    assert not fuv.is_structured_array(array1), 'array1 cannot be structured.'
    assert not fuv.is_structured_array(array2), 'array2 cannot be structured.'
    assert array1.shape == array2.shape, 'Inputs must be of the same shape.'
    # pylint: disable=len-as-condition
    assert len(array1.shape) > 0 and len(array1.shape) < 3, 'Only 1D or 2D.'
    are_equal = True
    if len(array1.shape) == 1:
        for i in range(array1.shape[0]):
            if np.isnan(array1[i]) and np.isnan(array2[i]):
                continue
            elif array1[i] != array2[i]:
                are_equal = False
                break
    elif len(array1.shape) == 2:
        for i in range(array1.shape[0]):
            for j in range(array1.shape[1]):
                if np.isnan(array1[i, j]) and np.isnan(array2[i, j]):
                    continue
                elif array1[i, j] != array2[i, j]:
                    are_equal = False
                    break
            if not are_equal:
                break
    return are_equal


def test_compare_nan_arrays():
    """
    Tests numpy arrays element-wise array comparison.
    """
    assertion_error_1 = 'array1 cannot be structured.'
    assertion_error_2 = 'array2 cannot be structured.'
    assertion_error_3 = 'Inputs must be of the same shape.'
    assertion_error_4 = 'Only 1D or 2D.'

    array_3d_a = np.ones((2, 2, 2), dtype=float)
    array_struct = np.array([(1, 1.)], dtype=[('a', int), ('b', float)])
    array_1d_a = np.array([1, np.nan, 3])
    array_1d_b = np.array([-np.inf, 5, np.inf])
    array_2d_a = np.array([[1, np.nan, 3], [-np.inf, 5, np.inf]])
    array_2d_b = np.array([[-np.inf, 5, np.inf], [1, np.nan, 3]])

    # Assertion error 1 -- structured array 1
    with pytest.raises(AssertionError) as exin:
        _compare_nan_arrays(array_struct, array_struct)
    assert str(exin.value).startswith(assertion_error_1)

    # Assertion error 2 -- structured array 2
    with pytest.raises(AssertionError) as exin:
        _compare_nan_arrays(array_1d_a, array_struct)
    assert str(exin.value).startswith(assertion_error_2)

    # Assertion error 3 -- different shapes
    with pytest.raises(AssertionError) as exin:
        _compare_nan_arrays(array_1d_a, array_2d_a)
    assert str(exin.value).startswith(assertion_error_3)

    # Assertion error 4 -- 3D array
    with pytest.raises(AssertionError) as exin:
        _compare_nan_arrays(array_3d_a, array_3d_a)
    assert str(exin.value).startswith(assertion_error_4)

    # 1D
    assert not _compare_nan_arrays(array_1d_a, array_1d_b)
    assert _compare_nan_arrays(array_1d_a, array_2d_a[0, :])
    assert not _compare_nan_arrays(array_1d_a, array_2d_a[1, :])
    assert not _compare_nan_arrays(array_1d_b, array_2d_a[0, :])
    assert _compare_nan_arrays(array_1d_b, array_2d_a[1, :])

    # 2D
    assert not _compare_nan_arrays(array_2d_a, array_2d_b)
    assert not _compare_nan_arrays(array_2d_a[[0], :], array_2d_b[[0], :])
    assert _compare_nan_arrays(array_2d_a, array_2d_b[[1, 0], :])
    assert _compare_nan_arrays(array_2d_a[[0], :], array_2d_b[[1], :])
    assert _compare_nan_arrays(array_2d_a[[1], :], array_2d_b[[0], :])


def test_fatf_structured_to_unstructured_row():
    """
    Tests :func:`fatf.utils.array_tools.fatf_structured_to_unstructured_row`.
    """
    type_error = 'The input should be a row of a structured array.'
    with pytest.raises(TypeError) as exin:
        fuat.fatf_structured_to_unstructured_row(
            np.array([b'123'], np.void)[0])
    assert str(exin.value) == type_error
    value_arror = ('structured_to_unstructured_row only supports conversion '
                   'of structured rows that hold base numpy types, i.e. '
                   'numerical and string-like -- numpy void and object-like '
                   'types are not allowed.')
    with pytest.raises(ValueError) as exin:
        fuat.fatf_structured_to_unstructured_row(NOT_BASE_STRUCTURED_ARRAY[0])
    assert str(exin.value) == value_arror

    simple = fuat.fatf_structured_to_unstructured_row(
        NUMERICAL_STRUCTURED_ARRAY[0])
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY[0])
    simple = fuat.fatf_structured_to_unstructured_row(
        NUMERICAL_STRUCTURED_ARRAY[2])
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY[2])
    simple = fuat.fatf_structured_to_unstructured_row(
        NUMERICAL_STRUCTURED_ARRAY[3])
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY[3])
    #
    simple = fuat.fatf_structured_to_unstructured_row(
        NOT_NUMERICAL_STRUCTURED_ARRAY[0])
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY[0])
    simple = fuat.fatf_structured_to_unstructured_row(
        NOT_NUMERICAL_STRUCTURED_ARRAY[6])
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY[6])
    simple = fuat.fatf_structured_to_unstructured_row(
        NOT_NUMERICAL_STRUCTURED_ARRAY[7])
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY[7])
    #
    simple = fuat.fatf_structured_to_unstructured_row(WIDE_STRUCTURED_ARRAY[0])
    assert _compare_nan_arrays(simple, WIDE_UNSTRUCTURED_ARRAY[0])
    simple = fuat.fatf_structured_to_unstructured_row(WIDE_STRUCTURED_ARRAY[2])
    assert _compare_nan_arrays(simple, WIDE_UNSTRUCTURED_ARRAY[2])

    assert fuat.fatf_structured_to_unstructured_row(
        np.array([(7, )], dtype=[('f', float)])[0]) == 7


def test_structured_to_unstructured_row():
    """
    Tests :func:`fatf.utils.array_tools.structured_to_unstructured_row`.
    """
    simple = fuat.fatf_structured_to_unstructured_row(
        NUMERICAL_STRUCTURED_ARRAY[2])
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY[2])
    assert fuat.fatf_structured_to_unstructured_row(
        np.array([(7, )], dtype=[('f', float)])[0]) == 7
    assert ('This function need not be tested as test_choose_structured_to_'
            'unstructured and test_fatf_structured_to_unstructured_row tests '
            'are sufficient and there is no straight forward way of testing '
            'it.')


def test_choose_structured_to_unstructured(caplog):
    """
    Tests :func:`fatf.utils.array_tools._choose_structured_to_unstructured`.
    """
    # pylint: disable=protected-access
    # Memorise current numpy version
    installed_numpy_version = np.version.version
    # Fake version lower than 1.16.0
    np.version.version = '1.15.999'
    log_message = ("Using fatf's fatf.utils.array_tools."
                   'fatf_structured_to_unstructured as fatf.utils.'
                   'array_tools.structured_to_unstructured and fatf.utils.'
                   'array_tools.fatf_structured_to_unstructured_row as '
                   'fatf.utils.array_tools.structured_to_unstructured_row.')
    assert fuat._choose_structured_to_unstructured()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].getMessage() == log_message
    # Fake at least 1.16.0 version
    np.version.version = '1.16.000'
    log_message = ("Using numpy's numpy.lib.recfunctions."
                   'structured_to_unstructured as fatf.utils.array_tools.'
                   'structured_to_unstructured and fatf.utils.array_tools.'
                   'structured_to_unstructured_row.')
    assert not fuat._choose_structured_to_unstructured()
    assert len(caplog.records) == 2
    assert caplog.records[1].levelname == 'INFO'
    assert caplog.records[1].getMessage() == log_message
    # Restore numpy version
    assert len(caplog.records) == 2
    np.version.version = installed_numpy_version


def test_fatf_structured_to_unstructured():
    """
    Tests :func:`fatf.utils.array_tools.fatf_structured_to_unstructured`.
    """
    # Wrong array types
    type_error = 'structured_array should be a structured numpy array.'
    with pytest.raises(TypeError) as exin:
        fuat.fatf_structured_to_unstructured(NUMERICAL_NP_ARRAY)
    assert str(exin.value) == type_error
    with pytest.raises(TypeError) as exin:
        fuat.fatf_structured_to_unstructured(NOT_NUMERICAL_NP_ARRAY)
    assert str(exin.value) == type_error
    with pytest.raises(TypeError) as exin:
        fuat.fatf_structured_to_unstructured(WIDE_NP_ARRAY)
    assert str(exin.value) == type_error

    # Arrays of complex-types
    value_error = ('fatf_structured_to_unstructured only supports conversion '
                   'of arrays that hold base numpy types, i.e. numerical and '
                   'string-like -- numpy void and object-like types are not '
                   'allowed.')
    complex_array = np.array([(None, object())],
                             dtype=[('n', 'O'), ('o', 'O')])
    with pytest.raises(ValueError) as exin:
        fuat.fatf_structured_to_unstructured(complex_array)
    assert str(exin.value) == value_error

    # Right type
    simple = fuat.fatf_structured_to_unstructured(NUMERICAL_STRUCTURED_ARRAY)
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY)
    simple = fuat.fatf_structured_to_unstructured(
        NOT_NUMERICAL_STRUCTURED_ARRAY)
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY)
    simple = fuat.fatf_structured_to_unstructured(WIDE_STRUCTURED_ARRAY)
    assert _compare_nan_arrays(simple, WIDE_UNSTRUCTURED_ARRAY)

    simple = fuat.fatf_structured_to_unstructured(
        np.array([(7, )], dtype=[('f', float)]))
    assert np.array_equal(simple, np.array([[7]]))
    simple = fuat.fatf_structured_to_unstructured(
        np.array([(4, ), (2, )], dtype=[('f', float)]))
    assert np.array_equal(simple, np.array([[4], [2]]))


def test_structured_to_unstructured():
    """
    Tests :func:`fatf.utils.array_tools.structured_to_unstructured`.
    """
    simple = fuat.structured_to_unstructured(NOT_NUMERICAL_STRUCTURED_ARRAY)
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY)
    simple = fuat.structured_to_unstructured(
        np.array([(7, )], dtype=[('f', float)]))
    assert _compare_nan_arrays(simple, np.array([[7]]))
    assert ('This function need not be tested as test_choose_structured_to_'
            'unstructured and test_fatf_structured_to_unstructured tests are '
            'sufficient and there is no straight forward way of testing it.')


def test_as_unstructured():
    """
    Tests :func:`fatf.utils.array_tools.as_unstructured`.
    """
    type_error = ('The input should either be a numpy (structured or '
                  'unstructured) array-like object (numpy.ndarray) or a row '
                  'of a structured numpy array (numpy.void).')
    value_error = ('as_unstructured only supports conversion of arrays that '
                   'hold base numpy types, i.e. numerical and string-like -- '
                   'numpy void and object-like types are not allowed.')
    # Test incompatible -- None -- type
    with pytest.raises(TypeError) as exin:
        fuat.as_unstructured(None)
    assert str(exin.value) == type_error

    # Test np.void -- a structured array's row
    simple = fuat.as_unstructured(NUMERICAL_STRUCTURED_ARRAY[0])
    assert _compare_nan_arrays(simple, NUMERICAL_UNSTRUCTURED_ARRAY[0])

    # Test structured array
    simple = fuat.as_unstructured(NOT_NUMERICAL_STRUCTURED_ARRAY)
    assert np.array_equal(simple, NOT_NUMERICAL_UNSTRUCTURED_ARRAY)
    # Test unstructured -- base type
    simple = fuat.as_unstructured(BASE_NP_ARRAY)
    assert np.array_equal(simple, BASE_NP_ARRAY)
    # Test unstructured -- not base type
    with pytest.raises(ValueError) as exin:
        fuat.as_unstructured(NOT_BASE_NP_ARRAY)
    assert str(exin.value) == value_error
