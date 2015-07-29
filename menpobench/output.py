from pathlib import Path
from menpobench.utils import save_json, load_json
from collections import namedtuple
from menpofit.fittingresult import plot_cumulative_error_distribution
from matplotlib import pyplot as plt

ErrorResult = namedtuple('ErrorResult', ['errors', 'path'])

def save_test_results(results, method_name, output_dir, matlab=False):
    json = {i: r.tojson() for i, r in results.items()}
    save_json(json, str(output_dir / '{}.json'.format(method_name)),
              pretty=True)
    if matlab:
        print('TODO: export .mat file here.')


def save_errors(gt_shapes, results, error_metrics, method_name, output_dir):
    final_shapes = [r.final_shape for r in results]
    json = {}
    for i, (error_name, error_metric) in enumerate(error_metrics):
        # error_name may be a path or a predefined
        name = '{}_{}'.format(i, Path(error_name).name.replace('.', '_'))
        errors = [float(error_metric(g, f))
                  for g, f in zip(gt_shapes, final_shapes)]
        json[name] = errors
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
