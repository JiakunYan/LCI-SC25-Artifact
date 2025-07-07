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
         label_order_fn=None, figsize=(4, 3),
         separate_legend=False):
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[tag_key, x_key])
    lines = parse_tag(df, x_key, y_key, tag_key)

    if label_order_fn:
        lines = sorted(lines, key=lambda x: label_order_fn(x["label"]))
        
    # handle 0
    if zero_x_is != 0:
        for line in lines:
            line["x"] = [zero_x_is if x == 0 else x for x in line["x"]]

    # fig, ax = plt.subplots(figsize=(8, 4))
    fig, ax = plt.subplots(figsize=figsize)
    fig_legend, ax_legend = plt.subplots()
    ax_legend.axis('off')
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
        label = line["label"]
        if label_fn:
            label = label_fn(label)
        marker = next(markers)
        line["marker"] = marker
        if with_error:
            line["error"] = [0 if math.isnan(x) else x for x in line["error"]]
            ax.errorbar(line["x"], line["y"], line["error"], label=label, marker=marker, markerfacecolor='white', capsize=3, markersize=8, linewidth=2, color=color, linestyle=linestyle)
        else:
            ax.plot(line["x"], line["y"], label=line["label"], marker=marker, markerfacecolor='white', markersize=8, linewidth=2, color=color, linestyle=linestyle)
    ax.set_xlabel(x_label)
    if position == "all" or position == "left":
        ax.set_ylabel(y_label)
    ax.set_xscale("log")
    ax.set_yscale("log")
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
        if not separate_legend:
            ax.legend(fontsize=12)
        else:
            lines1, labels1 = ax.get_legend_handles_labels()
            legend = fig_legend.legend(lines1, labels1, loc='center', ncol=10)
            legend.get_frame().set_linewidth(0)     # no border
            legend.get_frame().set_facecolor('none')
        # ax.legend()
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
    if separate_legend:
        fig_legend.savefig(output_png_name.replace(".png", "-legend.png"), bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        json.dump({"Time": lines, "Speedup": speedup_lines}, outfile)

def plot_bars(df, x_key, y_key, title,
              x_label=None, y_label=None,
              dirname=None, filename=None):
    if x_label is None:
        x_label = x_key
    if y_label is None:
        y_label = y_key

    df = df.sort_values(by=[x_key])
    data = parse_simple(df, x_key, y_key)

    fig, ax = plt.subplots()
    bar = ax.barh(data["x"], data["y"], xerr=data["error"], label=y_label)
    ax.barh(data["x"], np.array(data["y"]) * 0.08, left=data["y"], color="white")
    for i, rect in enumerate(bar):
        text = f'{data["y"][i]:.2f}'
        ax.text(data["y"][i], rect.get_y() + rect.get_height() / 2.0,
                text, ha='left', va='center')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if filename is None:
        filename = title

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}-bar.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')

def batch(df):
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    dirname = os.path.join(output_path, job_name)

    def rename_app(row):
        dict_app_name = {
            "lt-p\d+": "proc",
            "lt-t\d+-d1": "thrd-s",
            "lt-t\d+": "thrd-m",
            "bw-p64": "proc",
            "bw-p64-\d+": "proc",
            "bw-t64-\d+-d1": "thrd-s",
            "bw-t64-\d+": "thrd-m",
        }
        for key in dict_app_name.keys():
            if re.match(key, row["app_name"]):
                key = key
                break
        app_name = dict_app_name[key]

        return app_name
    df["app_name2"] = df.apply(rename_app, axis=1)
    
    def rename_rt(row):
        dict_rt_name = {
            "lci": "LCI",
            "mpi": "MPICH ofi",
            "mpi-ucx": "MPICH ucx",
            "cray-mpich": "Cray MPICH",
            "gex": "GASNet-EX",
        }
        rt_name = dict_rt_name[row["rt_name"]]
        return rt_name
    df["rt_name2"] = df.apply(rename_rt, axis=1)

    df["app_rt_name2"] = df.apply(lambda row:
                                  "{}-{}".format(row["app_name2"],
                                                 row["rt_name2"]),
                                  axis=1)

    def ncores(row):
        return row["ntasks_per_node"] * row["lcwpp:nthreads"]
    df["ncores"] = df.apply(ncores, axis=1)

    def color_fn(name):
        if "LCI" in name:
            return "tab:blue"
        elif "ucx" in name or "Cray" in name:
            return "tab:red"
        elif "GASNet" in name:
            return "tab:green"
        else:
            return "tab:orange"
    
    def linestyle_fn(name):
        if "thrd-s" in name:
            return "dotted"
        elif "thrd-m" in name:
            return "dashed"
        else:
            return "solid"
        
    def label_fn_for_thrd(name):
        if "thrd-m" in name:
            return ""
        elif "thrd-s" in name:
            return name[7:]
        else:
            print("Error: ", name)
            exit(1)
    
    def linestyle_fn_for_thrd(name):
        if "thrd-s" in name:
            return "dashed"
        else:
            return "solid"
        
    def label_order_fn(name):
        if "LCI" in name:
            return 0
        elif "GASNet-EX" in name:
            return 1
        elif "MPICH ofi" in name:
            return 2
        elif "MPICH ucx" in name:
            return 3
        elif "Cray MPICH" in name:
            return 4
        else:
            print("Error: ", name)
            exit(1)

    df["name2"] = df.apply(lambda row:
                          "{}-{}".format(row["app_name2"],
                                            row["rt_name2"]),
                          axis=1)
        

    ## messsage rate
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "lt" in row["app_name"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "ncores", "msg_rate(K/s)", "name2", None,
         dirname=dirname, filename="lt-all", with_error=True,
         x_label="Core Number", y_label="Message Rate (K/s)",
         color_fn=color_fn, linestyle_fn=linestyle_fn, figsize=(8, 4), 
         label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "lt" in row["app_name"] and
                          "proc" in row["app_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "ncores", "msg_rate(K/s)", "rt_name2", None,
         dirname=dirname, filename="lt-proc", with_error=True,
         x_label="Core Number", y_label="Message Rate (K/s)",
         color_fn=color_fn, label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "lt" in row["app_name"] and
                          (("thrd-m" in row["app_name2"] and
                          "Cray" not in row["rt_name2"] and
                          "GASNet" not in row["rt_name2"]) or
                          "thrd-s" in row["app_name2"]),
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "ncores", "msg_rate(K/s)", "app_rt_name2", None,
         dirname=dirname, filename="lt-thrd", with_error=True,
         x_label="Core Number", y_label="Message Rate (K/s)",
         color_fn=color_fn, linestyle_fn=linestyle_fn_for_thrd, 
         label_fn=label_fn_for_thrd, label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "lt" in row["app_name"] and
                          "thrd-m" in row["app_name2"] and
                          "Cray" not in row["rt_name2"] and
                          "GASNet" not in row["rt_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "ncores", "msg_rate(K/s)", "rt_name2", None,
         dirname=dirname, filename="lt-thrd-m", with_error=True,
         x_label="Core Number", y_label="Message Rate (K/s)",
         color_fn=color_fn, separate_legend=True, 
         label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "lt" in row["app_name"] and
                          "thrd-s" in row["app_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "ncores", "msg_rate(K/s)", "rt_name2", None,
         dirname=dirname, filename="lt-thrd-s", with_error=True,
         x_label="Core Number", y_label="Message Rate (K/s)",
         color_fn=color_fn, separate_legend=True, 
         label_order_fn=label_order_fn)
    
    # bandwidth
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "bw" in row["app_name"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "lcwpp:min_size", "bandwidth(MB/s)", "name2", None,
         dirname=dirname, filename="bw-all", with_error=True,
         x_label="Message Size", y_label="Bandwidth (MB/s)",
         color_fn=color_fn, linestyle_fn=linestyle_fn,
         figsize=(8, 4), label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "bw" in row["app_name"] and
                          "proc" in row["app_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "lcwpp:min_size", "bandwidth(MB/s)", "rt_name2", None,
         dirname=dirname, filename="bw-proc", with_error=True,
         x_label="Message Size", y_label="Bandwidth (MB/s)",
         color_fn=color_fn, label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "bw" in row["app_name"] and
                          (("thrd-m" in row["app_name2"] and
                          "Cray" not in row["rt_name2"] and
                          "GASNet" not in row["rt_name2"]) or
                          ("thrd-s" in row["app_name2"])),
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "lcwpp:min_size", "bandwidth(MB/s)", "app_rt_name2", None,
         dirname=dirname, filename="bw-thrd", with_error=True,
         x_label="Message Size", y_label="Bandwidth (MB/s)",
         color_fn=color_fn, linestyle_fn=linestyle_fn_for_thrd, 
         label_fn=label_fn_for_thrd, label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "bw" in row["app_name"] and
                          "thrd-m" in row["app_name2"] and
                          "Cray" not in row["rt_name2"] and
                          "GASNet" not in row["rt_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "lcwpp:min_size", "bandwidth(MB/s)", "rt_name2", None,
         dirname=dirname, filename="bw-thrd-m", with_error=True,
         x_label="Message Size", y_label="Bandwidth (MB/s)",
         color_fn=color_fn, separate_legend=True, label_order_fn=label_order_fn)
    
    df1_tmp = df[df.apply(lambda row:
                          row["ncores"] != 124 and
                          "bw" in row["app_name"] and
                          "thrd-s" in row["app_name2"],
                          axis=1)]
    df1 = df1_tmp.copy()
    plot(df1, "lcwpp:min_size", "bandwidth(MB/s)", "rt_name2", None,
         dirname=dirname, filename="bw-thrd-s", with_error=True,
         x_label="Message Size", y_label="Bandwidth (MB/s)",
         color_fn=color_fn, separate_legend=True, label_order_fn=label_order_fn)

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
