"""marianmt_comparison: controlled comparison of BPE, WordPiece, and
MoVoC-Tok pre-trained tokenizers under a shared MarianMT architecture.

This package is intentionally self-contained. It reads external tokenizer
artifacts (from the sibling `amseg` repository) strictly read-only by
absolute path; it does not import any code from that repository.
"""

__version__ = "0.1.0"
