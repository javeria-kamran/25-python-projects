## How to use:
### run these command as per your requirement
-python main.py /path/to/files --prefix "new_" --suffix "_v1"
python main.py /path/to/files \
    --replace "old" "new" \
    --seq --seq-start 100 \
    --timestamp \
    --title \
    --recursive \
    --dry-run

### Run this command if you wanna see which function do what:
python main.py --help