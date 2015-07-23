import menpo.io as mio


def save_test_results(results, method_name, methods_dir, matlab=False):
    print(matlab)
    mio.export_pickle(results, methods_dir / '{}.pkl'.format(method_name))
