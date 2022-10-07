# coding=utf-8
# Copyright Facebook and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tokenization classes for ESM."""
import os
from typing import List, Optional, Union

from ...tokenization_utils import PreTrainedTokenizer
from ...tokenization_utils_base import AddedToken
from ...utils import logging


logger = logging.get_logger(__name__)

VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt"}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "facebook/esm1b": "https://huggingface.co/facebook/esm1b/resolve/main/vocab.txt",
    },
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "facebook/esm1b": 1024,
}


def load_vocab_file(vocab_file):
    with open(vocab_file, "r") as f:
        lines = f.read().splitlines()
        return [l.strip() for l in lines]


class EsmTokenizer(PreTrainedTokenizer):
    """
    Constructs an ESM tokenizer.
    """

    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES
    model_input_names = ["input_ids", "attention_mask"]

    def __init__(self, vocab_file, **kwargs):
        super().__init__(**kwargs)
        self.all_tokens = load_vocab_file(vocab_file)
        self._id_to_token = {ind: tok for ind, tok in enumerate(self.all_tokens)}
        self._token_to_id = {tok: ind for ind, tok in enumerate(self.all_tokens)}
        self.unk_token = "<unk>"
        self.cls_token = "<cls>"
        self.pad_token = "<pad>"
        self.mask_token = "<mask>"
        self.eos_token = "<eos>"
        self.unique_no_split_tokens = self.all_tokens
        self._create_trie(self.unique_no_split_tokens)

    def _convert_id_to_token(self, index: int) -> str:
        return self._id_to_token.get(index, self.unk_token)

    def _convert_token_to_id(self, token: str) -> int:
        return self._token_to_id.get(token, self._token_to_id.get(self.unk_token))

    def _tokenize(self, text, **kwargs):
        return text.split()

    def get_vocab_size(self, with_added_tokens=False):
        return len(self._id_to_token)

    def token_to_id(self, token: str) -> int:
        return self._token_to_id.get(token, self._token_to_id.get(self.unk_token))

    def id_to_token(self, index: int) -> str:
        return self._id_to_token.get(index, self.unk_token)

    def build_inputs_with_special_tokens(
        self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None
    ) -> List[int]:
        if token_ids_1 is not None:
            raise ValueError("Multiple input sentences are not supported!")
        cls_: List[int] = [self.cls_token_id]
        eos_: List[int] = [self.eos_token_id]
        return cls_ + token_ids_0 + eos_

    def save_vocabulary(self, save_directory, filename_prefix):
        vocab_file = os.path.join(save_directory, (filename_prefix + "-" if filename_prefix else "") + "vocab.txt")
        with open(vocab_file, "w") as f:
            f.write("\n".join(self.all_tokens))
        return (vocab_file,)

    @property
    def vocab_size(self) -> int:
        return self.get_vocab_size(with_added_tokens=False)

    def _add_tokens(self, new_tokens: Union[List[str], List[AddedToken]], special_tokens: bool = False) -> int:
        return super()._add_tokens(new_tokens, special_tokens=True)