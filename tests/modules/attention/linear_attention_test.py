import torch
from numpy.testing import assert_almost_equal
import numpy as np
from torch.autograd import Variable
from torch.nn import Parameter

from allennlp.common.testing.test_case import AllenNlpTestCase
from allennlp.modules.attention import LinearAttention


class LinearAttentionTests(AllenNlpTestCase):

    def test_linear_similarity(self):
        linear = LinearAttention(3, 3)
        linear._weight_vector = Parameter(torch.FloatTensor([-.3, .5, 2.0, -1.0, 1, 1]))
        linear._bias = Parameter(torch.FloatTensor([.1]))
        output = linear(Variable(torch.FloatTensor([[[0, 0, 0]], [[-7, -8, -9]]])),
                        Variable(torch.FloatTensor([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])))

        assert_almost_equal(output.data.numpy(), np.array([[[4.1000], [17.4000]],
                                                           [[-9.8000], [36.6000]]]), decimal=2)


