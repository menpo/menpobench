function menpobench_matlab_train(method_path, training_images_path)

    menpobench_addpath_recurse(method_path);
    menpobench = menpobench_namespace();

    model = menpobench.train(training_images_path);
    save(fullfile(method_path, 'model.mat'));

    exit(0);
end