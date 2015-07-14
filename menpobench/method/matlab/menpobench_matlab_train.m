function menpobench_matlab_train(method_path, training_images_path)

    menpobench_addpath_recurse(method_path);
    menpobench = menpobench_namespace();

    display('Training method...');
    model = menpobench.train(training_images_path);

    display('Saving model...');
    save(fullfile(method_path, 'model.mat'), 'model');

    exit(0);
end
