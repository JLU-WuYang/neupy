import theano
import numpy as np
from scipy.sparse import csr_matrix

from neupy.utils import (preformat_value, as_array2d, AttributeKeyDict, asint,
                         smallest_positive_number, asfloat, format_data)
from neupy.network.utils import shuffle

from base import BaseTestCase


class UtilsTestCase(BaseTestCase):
    def test_preformat_value(self):
        def my_func():
            pass

        class MyClass(object):
            pass

        self.assertEqual('my_func', preformat_value(my_func))
        self.assertEqual('MyClass', preformat_value(MyClass))

        expected = ['my_func', 'MyClass', 1]
        actual = preformat_value((my_func, MyClass, 1))
        np.testing.assert_array_equal(expected, actual)

        expected = ['my_func', 'MyClass', 1]
        actual = preformat_value([my_func, MyClass, 1])
        np.testing.assert_array_equal(expected, actual)

        expected = sorted(['my_func', 'MyClass', 'x'])
        actual = sorted(preformat_value({my_func, MyClass, 'x'}))
        np.testing.assert_array_equal(expected, actual)

        self.assertEqual(1, preformat_value(1))

        expected = (3, 2)
        actual = preformat_value(np.ones((3, 2)))
        np.testing.assert_array_equal(expected, actual)

        expected = (1, 2)
        actual = preformat_value(np.matrix([[1, 1]]))
        np.testing.assert_array_equal(expected, actual)

    def test_shuffle(self):
        input_data = np.arange(10)
        shuffeled_data = shuffle(input_data, input_data)
        np.testing.assert_array_equal(*shuffeled_data)

        np.testing.assert_array_equal(tuple(), shuffle())

        with self.assertRaises(ValueError):
            shuffle(input_data, input_data[:len(input_data) - 1])

    def test_as_array2d(self):
        test_input = np.ones(5)
        actual_output = as_array2d(test_input)
        self.assertEqual((1, 5), actual_output.shape)

    def test_attribute_key_dict(self):
        attrdict = AttributeKeyDict(val1='hello', val2='world')

        # Get
        self.assertEqual(attrdict.val1, 'hello')
        self.assertEqual(attrdict.val2, 'world')

        with self.assertRaises(KeyError):
            attrdict.unknown_variable

        # Set
        attrdict.new_value = 'test'
        self.assertEqual(attrdict.new_value, 'test')

        # Delete
        del attrdict.val1
        with self.assertRaises(KeyError):
            attrdict.val1

    def test_smallest_positive_number(self):
        epsilon = smallest_positive_number()
        self.assertNotEqual(0, asfloat(1) - (asfloat(1) - asfloat(epsilon)))
        self.assertEqual(0, asfloat(1) - (asfloat(1) - asfloat(epsilon / 10)))

    def test_format_data(self):
        # None input
        self.assertEqual(format_data(None), None)

        # Sparse data
        sparse_matrix = csr_matrix((3, 4), dtype=np.int8)
        formated_sparce_matrix = format_data(sparse_matrix)
        np.testing.assert_array_equal(formated_sparce_matrix, sparse_matrix)
        self.assertEqual(formated_sparce_matrix.dtype, sparse_matrix.dtype)

        # Vector input
        x = np.random.random(10)
        formated_x = format_data(x, is_feature1d=True)
        self.assertEqual(formated_x.shape, (10, 1))

        x = np.random.random(10)
        formated_x = format_data(x, is_feature1d=False)
        self.assertEqual(formated_x.shape, (1, 10))

    def test_asfloat(self):
        float_type = theano.config.floatX

        # Sparse matrix
        sparse_matrix = csr_matrix((3, 4), dtype=np.int8)
        self.assertIs(sparse_matrix, asfloat(sparse_matrix))

        # Numpy array-like elements
        x = np.array([1, 2, 3], dtype=float_type)
        self.assertIs(x, asfloat(x))

        x = np.array([1, 2, 3], dtype=np.int8)
        self.assertIsNot(x, asfloat(x))

        # Python list
        x = [1, 2, 3]
        self.assertEqual(asfloat(x).shape, (3,))

        # Theano variables
        x = theano.tensor.imatrix()
        self.assertNotEqual(x.dtype, float_type)
        self.assertEqual(asfloat(x).dtype, float_type)

    def test_asint(self):
        int2float_types = {
            'float32': 'int32',
            'float64': 'int64',
        }
        int_type = int2float_types[theano.config.floatX]

        # Sparse matrix
        sparse_matrix = csr_matrix((3, 4), dtype=np.int8)
        self.assertIs(sparse_matrix, asint(sparse_matrix))

        # Numpy array-like elements
        x = np.array([1, 2, 3], dtype=int_type)
        self.assertIs(x, asint(x))

        x = np.array([1, 2, 3], dtype=np.int8)
        self.assertIsNot(x, asint(x))

        # Python list
        x = [1, 2, 3]
        self.assertEqual(asint(x).shape, (3,))

        # Theano variables
        x = theano.tensor.fmatrix()
        self.assertNotEqual(x.dtype, int_type)
        self.assertEqual(asint(x).dtype, int_type)
