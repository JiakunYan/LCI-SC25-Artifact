#!/usr/bin/env python3

import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import itertools
sys.path.append("../../../include")
from parse_simple import *
import numpy as np
import re
import math
import argparse
from pathlib import Path

job_name = None
output_path = "draw/"

def plot(df, x_key, y_key, tag_key, title,
         x_label=None, y_label=None,
         dirname=None, filename=None,
         label_fn=None, zero_x_is=0,
         base=None, smaller_is_better=True,
         with_error=True, position="all",
         color_fn=None, linestyle_fn=None,
         label_order=None):
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[tag_key, x_key])
    lines = parse_tag(df, x_key, y_key, tag_key)

    if label_order:
        lines = sorted(lines, key=lambda x: label_order.index
                       (x["label"]))

    # update labels
    if label_fn is not None:
        for line in lines:
            line["label"] = label_fn(line["label"])
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    # fig, ax = plt.subplots(figsize=(8, 4))
    fig, ax = plt.subplots(figsize=(4, 3))
    # Setup colors
    # cmap_tab20=plt.get_cmap('tab20')
    # ax.set_prop_cycle(color=[cmap_tab20(i) for i in chain(range(0, 20, 2), range(1, 20, 2))])
    markers = itertools.cycle(('D', 'o', 'v', '^', "<", ">", '+'))
    # time
    for line in lines:
        color = None
        if color_fn:
            color = color_fn(line["label"])
        linestyle = None
        if linestyle_fn:
            linestyle = linestyle_fn(line["label"])
        marker = next(markers)
        line["marker"] = marker
        if with_error:
            line["error"] = [0 if math.isnan(x) else x for x in line["error"]]
            ax.errorbar(line["x"], line["y"], line["error"], label=line["label"], marker=marker, markerfacecolor='white', capsize=3, markersize=8, linewidth=2, color=color, linestyle=linestyle)
        else:
            ax.plot(line["x"], line["y"], label=line["label"], marker=marker, markerfacecolor='white', markersize=8, linewidth=2, color=color, linestyle=linestyle)
    ax.set_xlabel(x_label)
    if position == "all" or position == "left":
        ax.set_ylabel(y_label)
    ax.set_xscale("log")
    # ax.set_yscale("log")
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
    # ax.yaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
    # ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))

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

def batch(df):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, job_name)

    def rename(row):
        dict_rt_name = {
            "lci-t\d+": "LCI",
            "gex-t\d+": "GASNet-EX",
            "gex-p1-t\d+": "GASNet-EX (p1)",
            "upcxx": "HipMer (UPC++)",
        }
        found = None
        for key in dict_rt_name.keys():
            if re.match(key, row["rt_name"]):
                found = key
                break
        rt_name = dict_rt_name[found]
        return rt_name
    df["name2"] = df.apply(rename, axis=1)
    df["throughput"] = df["avg_throughput"].apply(lambda x: x * 1e6)

    def color_fn(name):
        if "LCI" in name:
            return "tab:blue"
        elif "GASNet" in name:
            return "tab:orange"
        else:
            return "tab:red"
    
    ## lines
    df1_tmp = df[df.apply(lambda row:
                          (row["platform"] == "expanse" and row["name2"] != "GASNet-EX (p1)" or row["platform"] == "delta" and row["name2"] != "GASNet-EX") and # FIXME Platform: update platform name if necessary
                          row["avg_throughput"] > 0, axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "nnodes", "throughput", "name2", None,
         dirname=dirname, filename="kcount", with_error=True,
         x_label="Node Count", y_label="Throughput (Kmer/s)",
         color_fn=color_fn)

if __name__ == "__main__":
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to the directory containing raw slurm outputs.")
    args = parser.parse_args()

    job_name = Path(args.input).stem
    df = pd.read_csv(args.input)
    # interactive(df)
    batch(df)
