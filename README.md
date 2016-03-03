# ExileCUPItemProcessing

ExileCUPItemProcessing is a Python script which will intake a pricelist (included as _source.txt_) and output loot tables suitable for LootCompiler and pricelists/classlists suitable for your Exile mission config.cpp.

## Usage

The .txt files included are ready-to-use; if you're not interested in customizing the rarities of the items, or if you don't want to change which items are included, simply download _configcpp.txt_, _lootgroups.h.txt_, and _cupprices.txt_; these are the files containing configuration data for Exile.

If you are interested in changing things, you'll want to download _sources.txt_ and _cup.py_; put them in the same folder together. Modify _sources.txt_ to your liking (change classnames, prices and qualities of items), then run _cup.py_ (with, for instance, `python cup.py`).
