﻿# -*- coding: utf-8 -*-

from __future__ import division, print_function

import collections
import itertools
import numpy as np
import numpy.matlib
np.matlib = numpy.matlib
import pdb


def get_similarity_matrix_old(um):
    um = np.where(um == 0, um, 1)  # set all ratings to 1 ???
    # um = np.where(um >= 4, 1, 0)  # set all high ratings to 1
    ucount = um.shape[0]
    icount = um.shape[1]

    coratings = {i: collections.defaultdict(int) for i in range(icount)}
    for u in range(ucount):
        print('\r', u+1, '/', ucount, end='')
        items = np.nonzero(um[u, :])[0]
        for i in itertools.combinations(items, 2):
            coratings[i[0]][i[1]] += 1
            coratings[i[1]][i[0]] += 1
    # save_recommendation_data(coratings, 'coratings')
    # coratings = load_recommendation_data('coratings')

    not_coratings = {i: collections.defaultdict(int) for i in range(icount)}
    for i in coratings.keys():
        print('\r', i+1, '/', len(coratings), end='')
        not_rated_i = set(np.where(um[:, i] == 0)[0])
        for j in coratings[i].keys():
            rated_j = set(np.where(um[:, j] == 1)[0])
            not_coratings[i][j] = len(not_rated_i & rated_j)
    # # save_recommendation_data(not_coratings, 'not_coratings')
    # not_coratings = load_recommendation_data('not_coratings')

    # # debug helpers
    # self.rating_stats(um)
    # self.corating_stats(coratings, item_id=0)
    # self.ar_simple(um, coratings, 0, 2849)
    # self.ar_complex(um, coratings, 0, 2849)
    # self.ar_both(um, coratings, 0, 2849)

    sims = np.zeros((icount, icount))
    for x in range(icount):
        is_x = np.sum(um[:, x])
        not_x = um.shape[0] - is_x
        for y in coratings[x]:
            # # (x and y) / x  simple version
            # denominator = coratings[x][y]
            # numerator = is_x

            # ((x and y) * !x) / ((!x and y) * x)  complex version
            denominator = coratings[x][y] * not_x
            numerator = not_coratings[x][y] * is_x

            if numerator > 0:
                sims[x, y] = denominator / numerator

    return sims


def get_similarity_matrix(um):
    print(1)
    um.data = np.ones(um.data.shape[0])

    print(2)
    coratings = um.T.dot(um).toarray()
    np.fill_diagonal(coratings, 0)
    um = um.toarray()

    print(3)
    um_inv = np.copy(um)
    print(3.1)
    um_inv[um_inv == 0] = 2
    print(3.2)
    um_inv[um_inv == 1] = 0
    print(3.3)
    um_inv[um_inv == 2] = 1

    print(4)
    not_coratings = um_inv.T.dot(um)
    # icount = um.shape[1]
    # coratings_dense = self.load_recommendation_data('coratings')
    # tmp = scipy.sparse.dok_matrix((icount, icount))
    # for i in range(icount):
    #     print('\r', i+1, '/', icount, end='')
    #     for j in range(icount):
    #         tmp[i, j] = coratings_dense[i][j]
    # print()
    # tmp = tmp.toarray()
    # pdb.set_trace()

    # # debug helpers
    # self.rating_stats(um)
    # self.corating_stats(coratings, item_id=0)
    # self.ar_simple(um, coratings, 0, 2849)
    # self.ar_complex(um, coratings, 0, 2849)
    # self.ar_both(um, coratings, 0, 2849)

    print(5)
    col_sum = um.sum(axis=0)
    not_col_sum = um.shape[0] - col_sum

    # sims = np.zeros((icount, icount))
    # for x in range(icount):
    #     print('\r', x, end='')
    #     for y in range(icount):
    #         # # (x and y) / x  simple version
    #         # denominator = coratings[x, y]
    #         # numerator = col_sum[x]
    #
    #         # ((x and y) * !x) / ((!x and y) * x)  complex version
    #         denominator = coratings[x, y] * not_col_sum[x]
    #         numerator = not_coratings[x, y] * col_sum[x]
    #
    #         if numerator > 0:
    #             sims[x, y] = denominator / numerator

    print(6)
    col_sums = np.matlib.repmat(col_sum, coratings.shape[0], 1)
    not_col_sums = np.matlib.repmat(not_col_sum, not_coratings.shape[0], 1)

    print(7)
    denominator = coratings * not_col_sums.T
    numerator = not_coratings * col_sums.T

    print(8)
    sims = denominator / numerator
    sims[np.isnan(sims)] = 0
    sims[np.isinf(sims)] = 0

    return sims


if __name__ == '__main__':
    m = np.array([  # simple test case
        [5, 1, np.NAN, 2, 2, 4, 3, 2],
        [1, 5, 2, 5, 5, 1, 1, 4],
        [2, np.NAN, 3, 5, 4, 1, 2, 4],
        [4, 3, 5, 3, np.NAN, 5, 3, np.NAN],
        [2, np.NAN, 1, 3, np.NAN, 2, 5, 3],
        [4, 1, np.NAN, 1, np.NAN, 4, 3, 2],
        [4, 2, 1, 1, np.NAN, 5, 4, 1],
        [5, 2, 2, np.NAN, 2, 5, 4, 1],
        [4, 3, 3, np.NAN, np.NAN, 4, 3, np.NAN]
    ])

    # TODO: we need both dense and sparse here, I think