#!/usr/bin/env python3

import pandas as pd
import os,sys, json
from matplotlib import pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import itertools
import argparse
from pathlib import Path
sys.path.append("../../../include")
from draw_simple import *
from draw_bokeh import plot_bokeh
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

def plot_normalized_grouped_bars(df, app_key, runtime_key, attribute_key, metric_key, base_config,
                                 apps=None, configs=None, labels=None,
                                 title=None, x_label=None, y_label=None, x_ticklabels=None,
                                 dirname=None, filename=None):
    """
    Plot normalized grouped bars where each application's bars are normalized to its base configuration.
    
    Parameters:
    df: DataFrame with the data
    app_key: Column name for applications
    runtime_key: Column name for runtime configurations
    metric_key: Column name for the metric to plot
    base_config: The base runtime configuration to normalize against
    """
    # Get unique values
    if apps is None:
        apps = df[app_key].unique()
    else:
        apps = [app for app in apps if app in df[app_key].unique()]
    if configs is None:
        configs = df[runtime_key].unique()
    else:
        configs = [config for config in configs if config in df[runtime_key].unique()]
    if labels is None:
        labels = configs
    datapoints = []
    
    for app in apps:
        app_data = df[df[app_key] == app]

        attribute = app_data[attribute_key].iloc[0]
        if attribute in ["latency", "runtime"]:
            lower_is_better = True
        else:
            lower_is_better = False

        if base_config not in app_data[runtime_key].values:
            print(f"Warning: No data for {app} with {base_config}")
            return
        base_value = app_data[app_data[runtime_key] == base_config][metric_key].mean()
        for config in configs:
            data = app_data[app_data[runtime_key] == config][metric_key]
            if not data.empty:
                if lower_is_better:
                    normalized_data = base_value / data
                else:
                    normalized_data = data / base_value
                datapoints.append({
                    app_key: app,
                    runtime_key: config,
                    'mean': normalized_data.mean(),
                    'std': normalized_data.std()
                })
            else:
                print(f"Warning: No data for {app} with {config}")
                datapoints.append({
                    app_key: app,
                    runtime_key: config,
                    'mean': math.nan,
                    'std': math.nan
                })
    normalized_df = pd.DataFrame(datapoints)
    
    # Plotting
    n_groups = len(apps)
    n_configs = len(configs)
    width = 0.8 / n_configs
    
    # fig, ax = plt.subplots(figsize=(12, 6))
    fig, ax = plt.subplots(1, 1, figsize=(n_groups * (n_configs + 1) * 0.24 + 1, 3))
    
    # Plot bars for each configuration
    hatches = itertools.cycle(["/", "\\", "|", "-", "+", "x", ".", "*", "o", "O"])
    for i, config in enumerate(configs):
        positions = np.arange(n_groups) + i * width
        heights = [normalized_df[(normalized_df[app_key] == app) & 
                               (normalized_df[runtime_key] == config)]['mean'].iloc[0]
                  for app in apps]
        errors = [normalized_df[(normalized_df[app_key] == app) & 
                               (normalized_df[runtime_key] == config)]['std'].iloc[0]
                  for app in apps]
        # print(app, config, heights, errors)
        errors = [0 if math.isnan(x) else x for x in errors]
        bar = ax.bar(positions, heights, yerr=errors, width=width, label=labels[i], hatch=next(hatches))
        for j, rect in enumerate(bar):
            text = f' {heights[j]:.2f}'
            ax.text(rect.get_x() + rect.get_width() / 2.0, heights[j]   ,
                    text, ha='center', va='bottom', rotation=60)
    # Add horizontal line at y=1
    ax.axhline(y=1, color='black', linestyle='--', alpha=0.5)
    
    # Customize plot
    if y_label is None:
        y_label = f'Normalized Performance'
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    if title is not None:
        ax.set_title(title)
    ax.set_xticks(np.arange(n_groups) + (n_configs-1) * width/2)
    if x_ticklabels is None:
        x_ticklabels = apps
    ax.set_xticklabels(x_ticklabels)
    ax.set_ylim(ymin=0)

    lines1, labels1 = ax.get_legend_handles_labels()
    nrows = len(labels1) / 6.0
    ncols = math.ceil(len(labels1) / nrows)
    if nrows == 1:
        y_loc = 1
    else:
        y_loc = 1.02
    fig.legend(lines1, labels1, loc="center", bbox_to_anchor=(0.5, y_loc), ncols=ncols)

    plt.tight_layout()

    if title is None:
        title = "default"
    if filename is None:
        filename = title

    if not os.path.exists(dirname):
        os.mkdir(dirname)
    output_png_name = os.path.join(dirname, "{}.png".format(filename))
    fig.savefig(output_png_name, bbox_inches='tight')
    output_json_name = os.path.join(dirname, "{}.json".format(filename))
    with open(output_json_name, 'w') as outfile:
        normalized_df.to_json(outfile, orient='records')

def batch(df, job_name):
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
