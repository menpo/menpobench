function menpobench_matlab_fit(method_path, testing_images_path)

    menpobench_addpath_recurse(method_path);
    menpobench = menpobench_namespace();

    display('Setting up model...');
    model = menpobench.setup(method_path);

    display('Loading test data...');
    image_data_array = menpobench_read_images_struct(testing_images_path);
    n_images = length(image_data_array);

    results = cell(n_images, 1);
    menpobench_progressbar('Fitting test images: ');
    for i=1:n_images
        menpobench_progressbar((i / n_images) * 100);
        image_data = image_data_array{i}.pixels;
        bbox = image_data_array{i}.bbox;
        results{i} = menpobench.fit(image_data, bbox, model);
    end
    menpobench_progressbar('done');

    display('Saving results...');
    save(fullfile(testing_images_path, 'menpobench_test_results.mat'), 'results');

    exit(0);
end
