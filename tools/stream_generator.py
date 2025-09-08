import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import itertools
from pathlib import Path
import math
import os

# -------------------------------
# Default parameter options
# -------------------------------
video_params = {
    "Resolution": ["3840x2160", "1920x1080", "1280x720"],
    "Codec": ["libx264", "libx265", "mpeg1video", "mpeg2video", "vp9"],
    "Profile": ["main", "main10", "None"],
    "Framerate": [24, 30, 60],
    "Dynamic Range": ["SDR", "HDR"],
    "Bitrate": ["5000k", "18000k"]
}

audio_params = {
    "Codec": ["aac", "mp3", "ac3", "flac", "pcm_s16le"],
    "Sample Rate": [44100, 48000, 96000],
    "Channels": [1, 2, 6, 8],
    "Bitrate": ["128k", "256k", "512k", "1024k"]
}

fileformat_mapping = {
    "libx264": "h264",
    "libx265": "h265",
    "mpeg1video": "mpg",
    "mpeg2video": "mpg",
    "av1": "av1",
    "wmv": "wmv",
    "vp9":"vp9",
    "aac": "aac",
    "mp3": "mp3",
    "ac3": "ac3",
    "pcm_s16le": "wav",
    "flac": "flac",
    "wma": "wma"
}
video_test_sources = ["testsrc", "testsrc2", "smptebars", "rgbtestsrc", "pal100bars", "color_red", "color_blue", "color_green", "color_yellow", "color_white", "color_black"]
audio_test_sources = ["sine", "anoisesrc", "sweep"]

duration = 5  # seconds

# -------------------------------
# Generate and run FFmpeg commands
# -------------------------------
def run_ffmpeg(video_options, audio_options, video_enabled, audio_enabled, video_source,
               audio_source, input_files, durationEntry, gopSecEntry, keySecEntry, actualFileFormat, output_directory):
    if not video_enabled and not audio_enabled:
        messagebox.showwarning("Error", "Enable at least Video or Audio")
        return

    duration = int(durationEntry)
    gop_size_sec = float(gopSecEntry)
    key_sec = float(keySecEntry)

    # Prepare selected options
    vid_keys = list(video_params.keys())
    aud_keys = list(audio_params.keys())

    selected_vid_options = [video_options[k] for k in vid_keys]
    selected_aud_options = [audio_options[k] for k in aud_keys]

    # Generate all combinations
    vid_combos = list(itertools.product(*selected_vid_options)) if video_enabled else [()]
    aud_combos = list(itertools.product(*selected_aud_options)) if audio_enabled else [()]

    for vid_combo in vid_combos:
        for aud_combo in aud_combos:
            fileFormat = ""

            vid_dict = dict(zip(vid_keys, vid_combo)) if video_enabled else {}
            aud_dict = dict(zip(aud_keys, aud_combo)) if audio_enabled else {}

            if(video_enabled and vid_dict["Codec"] != "libx265" and vid_dict["Dynamic Range"] == "HDR"):
                continue

            if(actualFileFormat == None or actualFileFormat == ""):
                if(video_enabled and audio_enabled):
                    fileFormat = "mp4"
                elif(video_enabled):
                    fileFormat = fileformat_mapping[vid_dict["Codec"]]
                elif(audio_enabled):
                    fileFormat = fileformat_mapping[aud_dict["Codec"]]
            else:
                fileFormat = actualFileFormat

            # Output file naming
            parts = []
            if video_enabled:
                gop_size_frames = int(math.ceil(gop_size_sec * int(vid_dict["Framerate"])))
                key_frames = int(math.ceil(key_sec * int(vid_dict["Framerate"])))
                parts += [f"{v}" for k,v in vid_dict.items()]
            if audio_enabled:
                parts += [f"{v}" for k,v in aud_dict.items()]
            output_file = "vts_" + "_".join(parts) + "." + fileFormat

            if(output_directory == "" or output_directory == None):
                output_full_path = output_file
            else:
                output_full_path = os.path.join(output_directory, output_file)

            # Video input
            if input_files["video"]:
                video_input = f"-i {input_files['video']}"
            elif video_enabled:
                coloropt = ""
                if ("color" in video_source):
                    coloropt = ":c=" + video_source.split("_")[1]
                    video_source = "color"

                video_input = f"-f lavfi -i {video_source}=rate={vid_dict['Framerate']}:size={vid_dict['Resolution']}:duration={duration}{coloropt}"
            else:
                video_input = ""

            # Audio input
            if input_files["audio"]:
                audio_input = f"-i {input_files['audio']}"
            elif audio_enabled:
                if(audio_source == "sine"):
                    audio_input = f"-f lavfi -i {audio_source}=frequency=1000:sample_rate={aud_dict.get('Sample Rate',48000)}:duration={duration}"
                elif(audio_source == "anoisesrc"):
                    audio_input = f"-f lavfi -i {audio_source}=sample_rate={aud_dict.get('Sample Rate',48000)}:duration={duration}:c=pink"
                elif(audio_source == "sweep"):
                    audio_input = f"-f lavfi -i aevalsrc=sin(2*PI*(20+(20000-20)*t/10)*t):s={aud_dict.get('Sample Rate',48000)}"
            else:
                audio_input = ""

            cmd = ["ffmpeg", "-y"]
            if video_input: cmd += video_input.split()
            if audio_input: cmd += audio_input.split()
            if video_enabled:
                if(vid_dict["Codec"] == "libx264" or vid_dict["Codec"] == "libx265"):
                    if(vid_dict["Profile"] == "None"):
                        continue
                    cmd += ["-c:v", vid_dict["Codec"], "-profile:v", vid_dict["Profile"],
                            "-b:v", vid_dict["Bitrate"],
                            "-r", str(vid_dict["Framerate"])]
                else:
                    if(vid_dict["Profile"] != "None"):
                        continue
                    cmd += ["-c:v", vid_dict["Codec"],
                            "-b:v", vid_dict["Bitrate"],
                            "-r", str(vid_dict["Framerate"])]
                if(vid_dict["Dynamic Range"] == "HDR"):
                    cmd += ["-pix_fmt", "yuv420p10le", "-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc"]
                else:
                    cmd += ["-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]

                cmd += ["-g", str(gop_size_frames), "-keyint_min", str(key_frames), "-sc_threshold", "0"]

            if audio_enabled:
                cmd += ["-c:a", aud_dict["Codec"], "-ar", str(aud_dict["Sample Rate"]),
                        "-ac", str(aud_dict["Channels"]), "-b:a", aud_dict["Bitrate"]]
            cmd += ["-t", str(duration), output_full_path]

            print("Running:", " ".join(cmd))
            subprocess.run(cmd)

    messagebox.showinfo("Done", "Stream(s) generated successfully!")

# -------------------------------
# File selection
# -------------------------------
def select_file(file_type):
    path = filedialog.askopenfilename(title=f"Select {file_type} file")
    path = str(Path(path).resolve().as_posix())
    return path

# -------------------------------
# Folder selection
# -------------------------------
def select_folder(file_type):
    path = filedialog.askdirectory(title=f"Select {file_type} directory")
    if not path:
        return ""
    path = str(Path(path).resolve().as_posix())
    return path

# -------------------------------
# Build UI
# -------------------------------
root = tk.Tk()
root.title("VTS Test Stream Generator")
root.geometry("950x720")

# Global font style
style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TCheckbutton", font=("Segoe UI", 12))
style.configure("TEntry", font=("Segoe UI", 12))

# Enable toggles in a frame
toggle_frame = ttk.Frame(root, padding=10)
toggle_frame.pack(anchor='w', fill='x')

video_enabled = tk.BooleanVar(value=True)
audio_enabled = tk.BooleanVar(value=True)

ttk.Checkbutton(toggle_frame, text="Enable Video", variable=video_enabled).grid(row=0, column=0, sticky='w', padx=5, pady=5)
ttk.Checkbutton(toggle_frame, text="Enable Audio", variable=audio_enabled).grid(row=0, column=1, sticky='w', padx=15, pady=5)

# Duration row
duration_frame = ttk.Frame(root, padding=10)
duration_frame.pack(anchor='w', fill='x')

duration_var = tk.StringVar(value="10")  # default value
ttk.Label(duration_frame, text="Duration (sec):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
duration = ttk.Entry(duration_frame, textvariable=duration_var, width=10, font=("Segoe UI", 11))
duration.grid(row=0, column=1, sticky='w', padx=5, pady=5)

fileformat_var = tk.StringVar(value="mp4")  # default value
ttk.Label(duration_frame, text="File Format").grid(row=1, column=0, sticky='w', padx=5, pady=5)
file_format = ttk.Entry(duration_frame, textvariable=fileformat_var, width=10, font=("Segoe UI", 11))
file_format.grid(row=1, column=1, sticky='w', padx=5, pady=5)

output_path = tk.StringVar()

def select_directory():
    output_path.set(select_folder("Video"))

style = ttk.Style()
style.configure(
    "Customd.TButton",
    font=("Segoe UI", 11)
)

ttk.Button(duration_frame, text="Output Directory", command=select_directory, style="Customd.TButton").grid(
    row=2, column=0, padx=5, pady=5, sticky="w"
)
ttk.Label(duration_frame, textvariable=output_path, font=("Segoe UI", 10)).grid(
    row=2, column=1, sticky='w', padx=10, pady=8
)

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

style = ttk.Style()
style.configure("TNotebook", tabposition="n")  # tabs on top
style.configure("TNotebook.Tab", padding=[15, 8], font=("Segoe UI", 11, "bold"))

# Make active tab more visible
style.map("TNotebook.Tab",
          background=[("selected", "#d9d9d9")],
          expand=[("selected", [1, 1, 1, 0])])

# -------------------------------
# Video Parameters Tab
# -------------------------------
video_frame = ttk.Frame(notebook, padding=15, borderwidth=2, relief="groove")
notebook.add(video_frame, text="Video Parameters")

video_options = {}
row = 0
for key, options in video_params.items():
    ttk.Label(video_frame, text=key + ":", font=("Segoe UI", 12, "bold")).grid(
        row=row, column=0, sticky='w', padx=10, pady=8
    )
    vars_list = []
    col = 1
    for opt in options:
        var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(video_frame, text=str(opt), variable=var, font=("Segoe UI", 11))
        cb.grid(row=row, column=col, sticky='w', padx=5, pady=5)
        vars_list.append((opt, var))
        col += 1
    video_options[key] = [opt for opt, var in vars_list if var.get()]

    # Update function to collect selected options
    def update_vid_options(key=key, vars_list=vars_list):
        video_options[key] = [opt for opt, var in vars_list if var.get()]

    for _, var in vars_list:
        var.trace_add("write", lambda *args, key=key, vars_list=vars_list: update_vid_options(key, vars_list))

    row += 1

ttk.Label(video_frame, text="GOP Size (sec):", font=("Segoe UI", 12)).grid(
    row=row, column=0, sticky="w", padx=10, pady=8
)
gop_size_var = tk.StringVar(value="1")  # default value
gop_size_entry = ttk.Entry(video_frame, textvariable=gop_size_var, width=10, font=("Segoe UI", 11))
gop_size_entry.grid(
    row=row, column=1, sticky="w", padx=10, pady=8
)
row += 1

ttk.Label(video_frame, text="Keyframe Interval (sec):", font=("Segoe UI", 12)).grid(
    row=row, column=0, sticky="w", padx=10, pady=8
)
keyint_var = tk.StringVar(value="1")  # default value
keyint_entry = ttk.Entry(video_frame, textvariable=keyint_var, width=10, font=("Segoe UI", 11))
keyint_entry.grid(
    row=row, column=1, sticky="w", padx=10, pady=8
)
row += 1

# -------------------------------
# Audio Parameters Tab
# -------------------------------
audio_frame = ttk.Frame(notebook, padding=15, borderwidth=2, relief="groove")
notebook.add(audio_frame, text="Audio Parameters")

audio_options = {}
row = 0
for key, options in audio_params.items():
    ttk.Label(audio_frame, text=key + ":", font=("Segoe UI", 12, "bold")).grid(
        row=row, column=0, sticky='w', padx=10, pady=8
    )
    vars_list = []
    col = 1
    for opt in options:
        var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(audio_frame, text=str(opt), variable=var, font=("Segoe UI", 11))
        cb.grid(row=row, column=col, sticky='w', padx=5, pady=5)
        vars_list.append((opt, var))
        col += 1
    audio_options[key] = [opt for opt, var in vars_list if var.get()]

    def update_aud_options(key=key, vars_list=vars_list):
        audio_options[key] = [opt for opt, var in vars_list if var.get()]

    for _, var in vars_list:
        var.trace_add("write", lambda *args, key=key, vars_list=vars_list: update_aud_options(key, vars_list))

    row += 1

# -------------------------------
# Input / Test Sources Tab
# -------------------------------
input_frame = ttk.Frame(notebook, padding=15, borderwidth=2, relief="groove")
notebook.add(input_frame, text="Input / Test Sources")

ttk.Label(input_frame, text="Video Test Source:", font=("Segoe UI", 12)).grid(
    row=0, column=0, sticky='w', padx=10, pady=8
)
video_source_var = tk.StringVar(value=video_test_sources[0])
ttk.Combobox(input_frame, values=video_test_sources, textvariable=video_source_var, width=30, font=("Segoe UI", 11)).grid(
    row=0, column=1, padx=10, pady=8, sticky="w"
)

ttk.Label(input_frame, text="Audio Test Source:", font=("Segoe UI", 12)).grid(
    row=1, column=0, sticky='w', padx=10, pady=8
)
audio_source_var = tk.StringVar(value=audio_test_sources[0])
ttk.Combobox(input_frame, values=audio_test_sources, textvariable=audio_source_var, width=30, font=("Segoe UI", 11)).grid(
    row=1, column=1, padx=10, pady=8, sticky="w"
)

video_file_path = tk.StringVar()
audio_file_path = tk.StringVar()

def select_video_file():
    video_file_path.set(select_file("Video"))

def select_audio_file():
    audio_file_path.set(select_file("Audio"))

style = ttk.Style()
style.configure(
    "Customb.TButton",
    font=("Segoe UI", 12)
)

ttk.Button(input_frame, text="Select Video File", command=select_video_file, style="Customb.TButton").grid(
    row=2, column=0, padx=10, pady=8, sticky="w"
)
ttk.Label(input_frame, textvariable=video_file_path, font=("Segoe UI", 10)).grid(
    row=2, column=1, sticky='w', padx=10, pady=8
)

ttk.Button(input_frame, text="Select Audio File", command=select_audio_file, style="Customb.TButton").grid(
    row=3, column=0, padx=10, pady=8, sticky="w"
)
ttk.Label(input_frame, textvariable=audio_file_path, font=("Segoe UI", 10)).grid(
    row=3, column=1, sticky='w', padx=10, pady=8
)

# -------------------------------
# Generate Button
# -------------------------------
button_frame = ttk.Frame(root, padding=15)
button_frame.pack(fill="x")

style = ttk.Style()
style.configure(
    "Custom.TButton",
    font=("Segoe UI", 12, "bold")
)

generate_btn = ttk.Button(
    button_frame,
    text="🎬 Generate Stream(s)",
    command=lambda: run_ffmpeg(
        video_options,
        audio_options,
        video_enabled.get(),
        audio_enabled.get(),
        video_source_var.get(),
        audio_source_var.get(),
        {"video": video_file_path.get(), "audio": audio_file_path.get()},
        duration.get(),
        gop_size_entry.get(),
        keyint_entry.get(),
        file_format.get(),
        output_path.get()
    ),
    style="Custom.TButton"
)

generate_btn.pack(pady=10)

root.mainloop()
