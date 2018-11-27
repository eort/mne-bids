import numpy as np
from collections import OrderedDict as odict


class MockDataFrame():
    def __init__(self, data):
        """ A stripped down clone of a Pandas MockDataFrame object

        Parameters
        -----------
        data : ordered dictionary
            An ordered dictionary containing the column names (keys) and
            associated column values (values).

        Note: All data is cast as a string to ensure uniformity and to avoid
        issues when comparing data. Because of this, operations on the data
        in this format should be avoided and any processing done before
        assignment.

        """
        # create a mapping between the column names and the column number
        self.columns = odict(zip(data.keys(), range(len(data))))
        self._data = np.stack(data.values(), axis=-1).astype(str)

    def drop(self, values, column):
        """ Drop any rows with the specified values in the given column

        Parameters
        ----------
        values : list
            List of values to check for.
        column : str
            Name of the column to check values in.

        """
        # only need to drop values if there are some that need to be dropped
        if values != list():
            # if column not in self.columns we expect an error to be raised
            col_num = self.columns[column]
            # cast values to string type to be safe
            values = [str(i) for i in values]
            # create array with True values wherever the value is in values
            loc_data = np.where(np.isin(self._data, values))
            if col_num not in loc_data[1]:
                raise ValueError('values not found in column "%s"' % column)
            row_indexes = loc_data[0][np.where(loc_data[1] == col_num)]
            self._data = np.delete(self._data, row_indexes, 0)

    def append(self, other, drop_column=None):
        """ Add one MockDataFrame to another

        Parameters
        ----------
        other : MockDataFrame
            The other MockDataFrame object to be appended to the end of the
            current one.
        drop_column : str
            The name of the column to check for multiple instances of the same
            value. If multiple values are found in the column, the rows
            containing all but the last value are removed.

        """
        self._data = np.concatenate([self._data, other._data])
        if drop_column is not None:
            col_num = self.columns[drop_column]
            col_data = self._data[:, col_num]
            drop_indexes = np.where(col_data == other._data[0][col_num])[0]
            self._data = np.delete(self._data, drop_indexes[:-1], 0)

    def head(self, rows=5):
        """ Return a view of the first number of rows

        Parameters
        ----------
        rows : int
            Maximum number of rows to show

        """
        output = ''
        output += '\t'.join(list(self.columns.keys())) + '\n'
        count = min(rows, self._data.shape[0])
        for i in range(count):
            output += '\t'.join(self._data[i, :]) + '\n'
        if rows < self._data.shape[0]:
            output += '... (%s more rows)' % (self._data.shape[0] - rows)
        return output

    def __contains__(self, item):
        """ Provide functionality for the `in` operator

        item may be either an numpy.ndarray or a MockDataFrame, however it may
        only be 1 dimensional.

        """
        if isinstance(item, np.ndarray):
            return item.tolist() in self._data.tolist()
        elif isinstance(item, list):
            return item in self._data.tolist()
        elif isinstance(item, type(self)):
            return item._data.flatten().tolist() in self._data.tolist()

    def __getitem__(self, key):
        """ Return the data in the column specified """
        return self._data[:, self.columns[key]]

    def __repr__(self):
        """ String representation of the MockDataFrame """
        return self.head()

    @classmethod
    def from_tsv(cls, fname):
        """ Generate a MockDataFrame object from a .tsv file

        Parameters
        ----------
        fname : str
            Path to the tsv to be loaded.

        """
        # TODO: This could receive a list of data types to allow the data
        # type of the individual columns to be set correctly
        data = np.loadtxt(fname, dtype=str, delimiter='\t')
        # the first row will be the names
        column_names = data[0, :]
        info = data[1:, :]
        data_dict = odict()
        for i, name in enumerate(column_names):
            data_dict[name] = info[:, i]
        return cls(data_dict)

    def to_tsv(self, fname):
        """ Produce a tsv file

        Parameters
        ----------
        fname : str
            Path to the tsv to be generated.

        """
        header = '\t'.join(self.columns.keys())
        np.savetxt(fname, self._data, fmt='%s', delimiter='\t', header=header,
                   comments='')

    @property
    def data(self):
        return self._data