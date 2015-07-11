function menpobench_matlab_bridge(method_path, training_images_path)

    menpobench_addpath_recurse(method_path);
    model = menpobench_train(training_images_path);

    save(fullfile(method_path, 'model.mat'));

    exit(0);
end