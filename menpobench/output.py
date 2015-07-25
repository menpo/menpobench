from pathlib import Path
from menpobench.utils import save_json, load_json
from collections import namedtuple

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
    if _unique_stems([r.path for r in results]):
        # method names are unique across
        pass
    #
    metrics = results[0].errors.keys()
    for metric in metrics:
        pass


def plot_ced(methods_to_errors, error_metric_name, output_dir):
    # plot the ced and store it at the root.
    pass


def _unique_stems(paths):
    return len(set(p.stem for p in paths)) == len(paths)
