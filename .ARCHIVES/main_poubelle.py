"""
def translate(srt_filename, di, do):
    # Translate the files
    my_srt = srt()
    my_tr = translateLocally() # preconfigured with binary and model
    #srt_filename = join(di, subs_filename)
    html_input = srt_filename[:-3] + ".en.html" # replace srt by .en.html
    html_output = html_input[:-6] + ".fr.html" # replace en.html by .fr.html
    srt_output = join(do, srt_filename.replace(".srt",".fr.srt"))
    print(f"Actions: {srt_filename}\n  -> {html_input}\n  -> {html_output}\n  -> {srt_output}")
    my_srt.srt_to_html(srt_filename, html_input)
    my_tr.translate(html_input, html_output)
    my_srt.html_to_srt(html_output, srt_output)
    return srt_output

def set_subs_list(entry):
    list_files = []
    if isdir(entry):
        tmp = listdir(entry)
        for elem in tmp:
            elem_fullpath = join(entry, elem)
            if isfile(elem_fullpath) and elem.lower().endswith(['.mp4','.mkv']):
                list_files.append(elem_fullpath)
    elif isfile(entry) and entry.lower().endswith(['.mp4','.mkv']):
        list_files = [entry]
    return list_files

def extract_subs(list_files, di, do):
    subs_list = []
    ff_subs = FfmpegExtractSubs(config_cli.ffmpeg_path)
    for f in list_files:
        if f.lower().endswith(('.mkv','.mp4')):
            # the file name with full path
            mediafile_fullpath = join(di, f)
            print(f"Found {mediafile_fullpath}")
            # destination file name, full path and new extension
            subs_filename = f[:-3]+'srt'
            subs_fullpath = join(do, subs_filename)
            r = ff_subs.extract(source=mediafile_fullpath, destination=subs_fullpath, lang='', test=False)
            if r != FfmpegExtractSubs.E_NO_ERROR:
                print(f"Error stream not found; e={r}")
            print(f"  => output sub in {subs_fullpath}")
            subs_list.append(subs_filename)
    return subs_list

    list_files = []
# Case 1: a file is specified => takes priority
if fi is not None:
    list_files = set_subs_list(fi)
    # Check for an output file name / create one
    if fo is None:
        fo = fi[:-3]+"fr.srt"
# Case 2: a directory is specified
else:
    list_files = set_subs_list(di)
    # Check for an output folder name / create one
    if do is None:
        do = di

# Check what we found / close if empty
if not list_files:
    print(f"Nothing found at {di}")
    exit(ERR_INVALID_FOLDER)

subs_list = []
# Extraction of sub tracks
if run_extract:
    # Process filenames to extract subs from video files
    subs_list = extract_subs(list_files, di, do)

if not subs_list:
    print(f"No sub found")
    exit(ERR_NO_SUBS_FILE)

# Translation of sub tracks
if run_translate:
    # Now, go translate with the list of subs files
    for subs_filename in subs_list:
        translate(subs_filename, di, do)
"""