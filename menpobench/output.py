from pathlib import Path
from menpobench.utils import save_json


def save_test_results(results, method_name, methods_dir, matlab=False):
    json = {i: r.tojson() for i, r in results.items()}
    save_json(json, str(methods_dir / '{}.json'.format(method_name)),
              pretty=True)
    if matlab:
        print('TODO: export .mat file here.')


def calculate_errors(gt_shapes, results, error_metrics):
    final_shapes = [r.final_shape for r in results]
    name_to_errors = {}
    for i, (error_name, error_metric) in enumerate(error_metrics):
        # error_name may be a path or a predefined
        name = '{}_{}'.format(i, Path(error_name).name.replace('.', '_'))
        errors = [error_metric(g, f) for g, f in zip(gt_shapes, final_shapes)]
        name_to_errors[name] = errors
    return name_to_errors
