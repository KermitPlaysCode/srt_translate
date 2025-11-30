"""My CLI program to extract and translate subs"""

# Std lib
import argparse

# My libs
from lib_work import Work

# Retrieve filenames from CLI
cli = argparse.ArgumentParser()
cli.add_argument('-i','--input_video',
                 help="Folder to find MKV/MP4", default=None)
cli.add_argument('-o','--output_srt',
                 help="Folder to write SRT", default=None)
cli.add_argument('-e','--extract',
                 help="Action : extract", default=False, action='store_true')
cli.add_argument('-t','--translate',
                 help="Action : translate (default)", default=False, action='store_true')
cli.add_argument('-f','--input_sub',
                 help="Input SRT (takes precedence over -i)", default=None)
cli.add_argument('-F','--output_sub',
                 help="Output SRT (takes precedence over -o)", default=None)
args = cli.parse_args()

my_work = Work()

# Futur : enchainer extract et translate automatiquement

worksheet = my_work.prepare_work(args)
if worksheet['extract']:
    print("Action: extract")
    sublist = my_work.run_extract(worksheet)
elif worksheet['translate']:
    print("Action: translate")
    my_work.run_translate(worksheet)
print(worksheet)
# Job done
print("Complete")
