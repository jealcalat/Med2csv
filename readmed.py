""" How to use:
This function read MED raw files and writes csv files. MED files must have
the following conventions:

    1) All data should be stored in main variable {optional} as time.event.
       For example: if C is main variable, E is the counter, F is the timer and
       lever press is coded as 1, a lever press is stored in C in position E,
       C(E) = F + 0.1. If F = 120, C(E) = 120.1. Another main variable can be
       chosen, but I have only tested with C. Check variable 'a' in the function
       to see how it works the slicing from the start of C to its end.

    2) The number of columns should be specified. For example, if var cols is 5,
       which means the MED options PRINTCOLUMNS is the default, when we read a
       file with Pandas, it turns into a data frame with 6 columns. It will be
       named x1 to x6. The x1 is the column of row indexes in the raw; it'll be
       dropped. Then, the 6 cols will be stacked into two: (time, event). It
       should be easy to adapt the function to other conventions. If PRINTCOLUMNS
       is not the default (for example, is 2, which means we have a column for
       row names and a column for the data), this will produce a data frame with
       3 columns, from x1 to x3.
"""
import pandas as pd
import numpy as np


def read_med(file,
             phase,
             finfo,
             path_tidy,
             var_cols=5,
             col_n='C:'):
    """ Function to read-write MED raw data to csv
    :param file: String. The name of the file: path/to/file_name. Example:
           Windows: 'C:/some_folder/some_Med_file'
           Linux-Unix: '~/some_folder/some_Med_file'
    :param phase: Integer, string, or list of integer and string. For example,
           phase = 'A'; phase = 1; phase = ['A', 1] etc. The third case (the
           list ['A', 1]) is useful when having phase and conditions.
    :param finfo: A list with the following elements:
           subject, session in a list. Example ['034', 1]
    :param path_tidy: String. Where to store processed data frame.
    :param var_cols: The number of columns in PRINTCOLUMNS.
    :param col_n: String. Column to extract information. By default 'C:'.
    :return: None. Writes an csv of shape (n, 2) with t and event in the
             specified path_tidy. File name is a number; first position is
             is phase second is subject, from third onwards is the number
             of session.
    """

    # names parameter takes into account a data frame with ncols columns
    ncols = var_cols + 2
    df = pd.read_csv(file, delim_whitespace=True, header=None,
                     skiprows=3, names=['x' + str(i) for i in range(1, ncols)])

    subjf = finfo[0]
    session = finfo[1]

    a = np.where(df.x1 == "0:")[0]
    col_pos = np.where(df.x1 == col_n)[0]

    # Check whether subj name in fname and inside file is the same,
    # otherwise break and check fname for errors
    if len(col_pos) != 1:
        print(f'{col_n} is not unique, possible error in {finfo}. Dup file?')
        stop = True
    else:
        stop = False

    while not stop:
        col_idx = int(np.where(a == col_pos + 1)[0])
        start = a[col_idx]
        if a[col_idx] == a[-1]:
            end = len(df.index)
        else:
            end = a[col_idx + 1] - 2
        vC = df[start:(end + 1)].reset_index(drop=True)
        vC = vC.drop('x1', 1).stack().reset_index(drop=True)  # dropna default True

        vC = pd.DataFrame({'vC': vC.astype(str)})
        # separate time.event in two columns
        vC2 = vC['vC'].str.split('.', expand=True)

        # Make a string of phase if phase is a list
        if isinstance(phase, list):
            phase = ''.join([str(i) for i in phase])

        # File name to save in path_tidy. Fname is string of numbers.
        # See return in reference information.
        fsave = path_tidy + str(phase) + str(subjf) + str(session)
        vC2.to_csv(fsave + '.csv', index=False)
        # If saved, break while loop
        reach = True
        if reach:
            print(finfo)
            break


"""MIT License

Copyright (c) 2019 J.E. Alcalá

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""