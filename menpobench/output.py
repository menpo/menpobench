import numpy as np
from pathlib import Path
from collections import namedtuple
from menpobench.utils import save_json, load_json

ErrorResult = namedtuple('ErrorResult', ['errors', 'path'])


def save_test_results(results, method_name, output_dir, matlab=False):
    save_json(results, str(output_dir / '{}.json'.format(method_name)),
              pretty=True)
    if matlab:
        print('TODO: export .mat file here.')


def compute_and_save_errors(results, error_metrics, method_name, output_dir):
    json = {}
    for error_name, error_metric in error_metrics:
        # error_name may be a path or a predefined
        name = Path(error_name).name.replace('.', '_')
        json[name] = [float(error_metric(np.array(r['gt']),
                                         np.array(r['result']['final'])))
                      for r in results.values()]
    save_json(json, str(output_dir / '{}.json'.format(method_name)),
              pretty=True)


def plot_ceds(output_dir):
    results = [ErrorResult(load_json(e), e)
               for e in (output_dir / 'errors').glob('**/*.json')]
    metrics = results[0].errors.keys()
    for metric in metrics:
        errors, method_names = [], []
        for result in results:
            method_names.append(result.path.stem)
            errors.append(result.errors[metric])
        plot_ced(errors, method_names, metric, output_dir)


def plot_ced(errors, method_names, error_metric_name, output_dir):
    from matplotlib import pyplot as plt
    from menpofit.result import plot_cumulative_error_distribution
    # plot the ced and store it at the root.
    plot_cumulative_error_distribution(errors, legend_entries=method_names,
                                       error_range=(0, 0.05, 0.005))
    # shift the main graph to make room for the legend
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    plt.savefig(str(output_dir / '{}.pdf'.format(error_metric_name)))
    plt.clf()


def _unique_stems(paths):
    return len(set(p.stem for p in paths)) == len(paths)
