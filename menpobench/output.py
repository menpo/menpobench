from menpobench.utils import save_json


def save_test_results(results, method_name, methods_dir, matlab=False):
    json = {i: r.tojson() for i, r in results.items()}
    save_json(json, str(methods_dir / '{}.json'.format(method_name)),
              pretty=True)
    if matlab:
        print('TODO: export .mat file here.')
