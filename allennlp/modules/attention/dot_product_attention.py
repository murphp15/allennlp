"""
A ``Module`` that takes two matrices as input and returns a matrix of attentions.
"""

import torch
from overrides import overrides
from allennlp.common import Params
from allennlp.modules.attention.legacy_attention import Attention


@Attention.register("dot_product")
class DotProductAttention(Attention):

    @overrides
    def _forward_internal(self,
                          vector: torch.Tensor,
                          matrix: torch.Tensor,
                          matrix_mask: torch.Tensor = None) -> torch.Tensor:
        # pylint: disable=arguments-differ
        return vector.unsqueeze(1).bmm(matrix.transpose(2, 1)).squeeze(1)

    @classmethod
    def from_params(cls, params: Params):
        normalize = params.pop_bool('normalize', True)
        params.assert_empty(cls.__name__)
        return DotProductAttention(normalize)
