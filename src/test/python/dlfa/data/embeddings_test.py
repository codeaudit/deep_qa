# pylint: disable=no-self-use

import gzip
import numpy
import pytest

from pyfakefs import fake_filesystem_unittest

from dlfa.data.embeddings import PretrainedEmbeddings
from dlfa.data.data_indexer import DataIndexer

class TestPretrainedEmbeddings(fake_filesystem_unittest.TestCase):
    # pylint: disable=invalid-name
    def setUp(self):
        self.setUpPyfakefs()

    def test_get_embedding_layer_uses_correct_embedding_size(self):
        data_indexer = DataIndexer()
        embeddings_filename = "/embeddings.gz"
        with gzip.open(embeddings_filename, 'wb') as embeddings_file:
            embeddings_file.write("word1 1.0 2.3 -1.0\n".encode('utf-8'))
            embeddings_file.write("word2 0.1 0.4 -4.0\n".encode('utf-8'))
        embedding_layer = PretrainedEmbeddings.get_embedding_layer(embeddings_filename,
                                                                   data_indexer)
        assert embedding_layer.output_dim == 3

        with gzip.open(embeddings_filename, 'wb') as embeddings_file:
            embeddings_file.write("word1 1.0 2.3 -1.0 3.1\n".encode('utf-8'))
            embeddings_file.write("word2 0.1 0.4 -4.0 -1.2\n".encode('utf-8'))
        embedding_layer = PretrainedEmbeddings.get_embedding_layer(embeddings_filename,
                                                                   data_indexer)
        assert embedding_layer.output_dim == 4

    def test_get_embedding_layer_crashes_on_changing_embedding_size(self):
        data_indexer = DataIndexer()
        embeddings_filename = "/embeddings.gz"
        with gzip.open(embeddings_filename, 'wb') as embeddings_file:
            embeddings_file.write("dimensionality 3".encode('utf-8'))
            embeddings_file.write("word1 1.0 2.3 -1.0\n".encode('utf-8'))
            embeddings_file.write("word2 0.1 0.4 -4.0\n".encode('utf-8'))
        with pytest.raises(Exception):
            PretrainedEmbeddings.get_embedding_layer(embeddings_filename, data_indexer)

    def test_get_embedding_layer_actually_initializes_word_vectors_correctly(self):
        data_indexer = DataIndexer()
        data_indexer.add_word_to_index("word")
        embeddings_filename = "/embeddings.gz"
        with gzip.open(embeddings_filename, 'wb') as embeddings_file:
            embeddings_file.write("word 1.0 2.3 -1.0\n".encode('utf-8'))
        embedding_layer = PretrainedEmbeddings.get_embedding_layer(embeddings_filename,
                                                                   data_indexer)
        word_vector = embedding_layer.initial_weights[0][data_indexer.get_word_index("word")]
        assert numpy.allclose(word_vector, numpy.asarray([1.0, 2.3, -1.0]))

    def test_get_embedding_layer_initializes_unseen_words_randomly_not_zero(self):
        data_indexer = DataIndexer()
        data_indexer.add_word_to_index("word2")
        embeddings_filename = "/embeddings.gz"
        with gzip.open(embeddings_filename, 'wb') as embeddings_file:
            embeddings_file.write("word 1.0 2.3 -1.0\n".encode('utf-8'))
        embedding_layer = PretrainedEmbeddings.get_embedding_layer(embeddings_filename,
                                                                   data_indexer)
        word_vector = embedding_layer.initial_weights[0][data_indexer.get_word_index("word2")]
        assert not numpy.allclose(word_vector, numpy.asarray([0.0, 0.0, 0.0]))