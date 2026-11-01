# Mizo (Lushai) number ↔ words

Bidirectional conversion between whole numbers **0 … 9,999,999,999** and Mizo cardinal number words.

No third-party dependencies — Python 3.10+ stdlib only.

## Quick start

```bash
python main.py to-words 42
# sawmli pahnih

python main.py to-words 1000000
# maktaduai

python main.py to-number sawmhnih pahnih
# 22

python main.py roundtrip 9999999999
from mizo_numberwords import number_to_words, words_to_number

number_to_words(115)           # 'za sawmpanga'
words_to_number("sangkhat")    # 1000
