#!/usr/bin/env python3

import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import itertools
import argparse
from pathlib import Path
sys.path.append("../../../include")
from parse_simple import *
import numpy as np
import math
from ast import literal_eval

job_name = None
# input_path = "data/"
output_path = "draw/"

def plot_lines(df, x_key, y_key, tag_keys, title=None,
         x_label=None, y_label=None,
         dirname=None, filename=None,
         label_fn=None, zero_x_is=0,
         y_minor_formatter=None, x_minor_formatter=None,
         base=None, smaller_is_better=True,
         xscale="log", yscale="log",
         with_error=True, position="all"):
    if df.empty:
        return
    if type(tag_keys) is list:
        tag_key = "-".join(tag_keys)
        df[tag_key] = df[tag_keys].agg('-'.join, axis=1)
    else:
        tag_key = tag_keys
    
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[tag_key, x_key])
    lines = parse_tag(df, x_key, y_key, tag_key)

    # update labels
    if label_fn is not None:
        for line in lines:
            line["label"] = label_fn(line["label"])
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    fig, ax = plt.subplots(figsize=(4, 3))
    # Setup colors
    # cmap_tab20=plt.get_cmap('tab20')
    # ax.set_prop_cycle(color=[cmap_tab20(i) for i in chain(range(0, 20, 2), range(1, 20, 2))])
    markers = itertools.cycle(('D', 'o', 'v', ',', '+'))
    # time
    for line in lines:
        marker = next(markers)
        line["marker"] = marker
        if with_error:
            line["error"] = [0 if math.isnan(x) else x for x in line["error"]]
            ax.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=marker, markerfacecolor='white', capsize=3, markersize=8, linewidth=2)
        else:
            ax.plot(line["x"], line["y"], label=line["label"], marker=marker, markerfacecolor='white', markersize=8, linewidth=2)
    ax.set_xlabel(x_label)
    if position == "all" or position == "left":
        ax.set_ylabel(y_label)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    if title:
        ax.set_title(title)
    # ax.legend(bbox_to_anchor = (1.05, 0.6))
    # ax.legend(bbox_to_anchor=(1.01, 1.01))

    # speedup
    baseline = None
    ax2 = None
    speedup_lines = None
    for line in lines:
        if base == line["label"]:
            baseline = line
            break
    if baseline:
        ax2 = ax.twinx()
        speedup_lines = []
        for line in lines:
            if line['label'] == baseline['label']:
                ax2.plot(line["x"], [1 for x in range(len(line["x"]))], linestyle='dotted')
                continue
            if smaller_is_better:
                speedup = [float(x) / float(b) for x, b in zip(line["y"], baseline["y"])]
                label = "{} / {}".format(line['label'], baseline['label'])
            else:
                speedup = [float(b) / float(x) for x, b in zip(line["y"], baseline["y"])]
                label = "{} / {}".format(baseline['label'], line['label'])
            speedup_lines.append({"label": line["label"], "x": line["x"], "y": speedup})
            ax2.plot(line["x"][:len(speedup)], speedup, label=label, marker=line["marker"], markerfacecolor='white', linestyle='dotted', markersize=8, linewidth=2)
        if position == "all" or position == "right":
            ax2.set_ylabel("Speedup")
    # ax2.legend()

    # ask matplotlib for the plotted objects and their labels
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
    if ax2:
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(0, 1.2), ncol=3, fancybox=True)
    else:
        ax.legend()
    ax.tick_params(axis='y', which='both')
    if y_minor_formatter:
        ax.yaxis.set_minor_formatter(y_minor_formatter)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    if x_minor_formatter:
        ax.xaxis.set_minor_formatter(x_minor_formatter)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))

    plt.tight_layout()

    if filename is None:
        filename = title

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines, "Speedup": speedup_lines}, outfile)

def batch(df, job_name):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, job_name)


    df['label'] = df.apply(lambda row: 'lci' if row['rt_name'] == 'lci2' else 
                                 'mpi' if row['rt_name'] == 'mpi' else 
                                 'mpix', axis=1)

    # octotiger
    df['timesteps'] = df['timesteps'].str.split(' ')
    df['timesteps'] = df['timesteps'].apply(lambda x: [float(i) for i in x] if type(x) == list else x)
    df = df.explode('timesteps')
    # octotiger
    df1_tmp = df[df.apply(lambda row:
                          row["app_name"] == "octotiger",
                          axis=1)]
    df1 = df1_tmp.copy()
    plot_lines(df1, "nnodes", "timesteps", "label",
               dirname=dirname, filename="octotiger", with_error=True, 
               x_label="Node Count", y_label="Time (s) per step",)
    
    # FFT
    df2_tmp = df[df.apply(lambda row:
                          row["app_name"] == "fft",
                          axis=1)]
    df2 = df2_tmp.copy()
    plot_lines(df2, "nnodes", "value", "label",
               dirname=dirname, filename="fft", with_error=True,
               x_label="Node Count", y_label="Time (s)",)


if __name__ == "__main__":
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to the directory containing raw slurm outputs.")
    args = parser.parse_args()

    job_name = Path(args.input).stem

    df = pd.read_csv(args.input)
    # interactive(df)
    batch(df, job_name)
