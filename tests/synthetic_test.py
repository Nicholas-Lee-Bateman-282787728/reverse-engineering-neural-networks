# Copyright 2020 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for synthetic datasets."""

from renn.data import synthetic
import numpy as np


def test_constant_sampler():
  """Tests that the constant sampler returns
  an array of the specified length, with the single
  specified value"""
  constant_values = [4, 23, 45, 1, 94]
  sample_nums = [10, 15, 16, 18]

  for val in constant_values:
    s, max_length = synthetic.constant_sampler(value=val)
    assert max_length == val
    for num in sample_nums:
      assert len(s(num)) == num
      assert len(set(s(num))) == 1
      assert s(num)[0] == val


def test_uniform_sampler():
  """Tests that the uniform sampler returns
  samples of the proper length, whose values lie in the
  specified interval"""
  intervals = [(10, 20), (15, 30)]
  sample_nums = [10, 15, 16, 18]

  for interval in intervals:
    s, max_length = synthetic.uniform_sampler(min_val=interval[0],
                                              max_val=interval[1])
    assert max_length == interval[1]
    for num in sample_nums:
      samples = s(num)
      assert len(samples) == num

      for sample in samples:
        assert sample <= interval[1] and sample >= interval[0]


def test_scoring():
  """Tests that the scoring function works correctly,
  specifically that it uses the length properly"""

  test_dataset = synthetic.Unordered(num_classes=3)

  SYMBOL = 0
  SYMBOL_SCORE = test_dataset.vocab[SYMBOL]

  MAX_LENGTH = 100
  MIN_LENGTH = 10

  for symbol, symbol_score in test_dataset.vocab.items():

    test_sentence = [symbol] * MAX_LENGTH

    for length in range(MIN_LENGTH, MAX_LENGTH):
      calculated_score = test_dataset.score(test_sentence, length)
      assert np.array_equal(calculated_score, symbol_score * length)


def test_batching():
  """Tests that batch['inputs'] has the correct shape,
  and batch['index'] matches the length of the sequence,
  in the easy-to-check case of a uniform sampler."""

  LENGTH = 30
  BATCH_SIZE = 64
  test_dataset = synthetic.Unordered(num_classes=3,
                                     batch_size=BATCH_SIZE,
                                     length_sampler='Constant',
                                     sampler_params={'value': LENGTH})
  test_batch = next(test_dataset)
  assert np.array_equal(test_batch['inputs'].shape,
                        np.array([BATCH_SIZE, LENGTH]))

  # check that index is always LENGTH
  assert len(test_batch['index']) == BATCH_SIZE
  assert len(set(test_batch['index'])) == 1
  assert test_batch['index'][0] == LENGTH
