# pylint: disable=no-self-use,invalid-name
from typing import List, Any
from collections import Counter

from allennlp.common import Params
from allennlp.common.testing import AllenNlpTestCase
from allennlp.data import Instance, Token, Vocabulary
from allennlp.data.dataset_readers.dataset_reader import _LazyInstances
from allennlp.data.fields import TextField, MetadataField
from allennlp.data.iterators.simple_partition_iterator import SimplePartitionIterator
from allennlp.data.token_indexers import SingleIdTokenIndexer

class TestSimplePartitionIterator(AllenNlpTestCase):
    def setUp(self):
        super().setUp()
        self.token_indexers = {"tokens": SingleIdTokenIndexer()}
        self.vocab = Vocabulary()
        self.this_index = self.vocab.add_token_to_namespace('this')
        self.is_index = self.vocab.add_token_to_namespace('is')
        self.a_index = self.vocab.add_token_to_namespace('a')
        self.sentence_index = self.vocab.add_token_to_namespace('sentence')
        self.another_index = self.vocab.add_token_to_namespace('another')
        self.yet_index = self.vocab.add_token_to_namespace('yet')
        self.very_index = self.vocab.add_token_to_namespace('very')
        self.long_index = self.vocab.add_token_to_namespace('long')
        def instances(i: int):
            return [
                    self.create_instance(["this", "is", "a", "sentence"], i),
                    self.create_instance(["this", "is", "another", "sentence"], i),
                    self.create_instance(["yet", "another", "sentence"], i),
                    self.create_instance(["this", "is", "a", "very", "very", "very", "very", "long", "sentence"], i),
                    self.create_instance(["sentence"], i)
            ][:(i+1)]

        self.instances: List[Instance] = []
        for i in range(5):
            self.instances.extend(instances(i))
        for i in range(5):
            self.instances.extend(instances(i))
        # Should be 1, 2, 3, 4, 5, 1, 2, 3, 4, 5

    def create_instance(self, str_tokens: List[str], metadata: Any) -> Instance:
        tokens = [Token(t) for t in str_tokens]
        metadata = MetadataField({'meta': metadata})
        instance = Instance({'text': TextField(tokens, self.token_indexers),
                             'metadata': metadata})
        instance.index_fields(self.vocab)
        return instance

    def assert_instances_are_correct(self, candidate_instances):
        # First we need to remove padding tokens from the candidates.
        # pylint: disable=protected-access
        candidate_instances = [tuple(w for w in instance if w != 0) for instance in candidate_instances]
        expected_instances = [tuple(instance.fields["text"]._indexed_tokens["tokens"])
                              for instance in self.instances]
        assert set(candidate_instances) == set(expected_instances)

    def test_partitioning(self):
        iterator = SimplePartitionIterator(max_instances_in_memory=6, partition_key="meta")
        batches = [batch for batch in iterator(self.instances, num_epochs=1)]

        assert len(batches) == 10
        assert [len(batch['metadata']) for batch in batches] == [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
