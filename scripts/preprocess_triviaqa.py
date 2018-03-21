"""
Takes the raw `triviaqa-rc.tar.gz` (or an untarred version of it)
and converts it into two JSONL files: `web-train.jsonl` and `web-dev.jsonl`.

Each JSON line corresponds to a single question and has the format

{
    "id": "qw_1934",
    "text": "what is the ... ?",
    "tokens": [["what", 0], ...],
    "paragraphs": {
        "text": ["first paragraph...", "second paragraph", ...],
        "tokens": [[["first", 0], ...], ...],
        "token_spans": [[[62, 63]], ...],
        "has_answers": [0],
    },
    "answer_texts": ["primary answer", "alternative answer"]
}
"""

from typing import List
import json
import logging
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir))))
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    level=logging.INFO)

from allennlp.common import Params
from allennlp.common.util import lazy_groups_of
from allennlp.data import Instance
from allennlp.data.tokenizers import Tokenizer
from allennlp.data.tokenizers.token import Token, token_to_json, json_to_token
from allennlp.data.dataset_readers.reading_comprehension import util
from allennlp.data.dataset_readers.reading_comprehension.triviaqa import MergeAndSorter, Question, MergedParagraphs, preprocess
from allennlp.data.vocabulary import Vocabulary

logger = logging.getLogger(__name__)

def main(params: Params, triviaqa_path: pathlib.Path, outdir: pathlib.Path):
    outdir.mkdir(exist_ok=True)

    # If triviaqa is a tar.gz, then untar it to a temporary location:
    if triviaqa_path.is_dir():
        # Given a directory, so do nothing.
        logger.info(f"{triviaqa_path} is a directory, so no un-tar-ing to do.")
        tempdir = None
    else:
        # Make a new tempdir, untar the dataset, and store the location.
        tempdir = tempfile.mkdtemp()
        logger.info(f"Un-tar-ing {triviaqa_path} to {tempdir}")
        with tarfile.open(triviaqa_path) as tarball:
            tarball.extractall(tempdir)
        triviaqa_path = pathlib.Path(tempdir)

    tokenizer = Tokenizer.from_params(params.pop('tokenizer', {}))

    for questions_file, topn in [('web-train.json', 4),
                                 ('web-dev.json', 15)]:
        logger.info(f"starting questions file {questions_file}")

        output_path = outdir / f"{questions_file}l"

        with open(output_path, 'w') as f:
            for question in preprocess(triviaqa_path, questions_file, topn, tokenizer):
                f.write(question.to_json())
                f.write("\n")

    # And then finally clean up:
    if tempdir is not None:
        logger.info(f"cleaning up tempdir {tempdir}")
        shutil.rmtree(tempdir)

if __name__ == '__main__':
    params = Params.from_file(sys.argv[1])
    triviaqa_path = pathlib.Path(sys.argv[2])
    outdir = pathlib.Path(sys.argv[3])
    main(params, triviaqa_path, outdir)