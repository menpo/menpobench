function menpobench_matlab_fit(method_path, testing_images_path)

    menpobench_addpath_recurse(method_path);
    menpobench = menpobench_namespace();

    model = menpobench.setup(method_path);

    image_data_array = menpobench_read_images_struct(testing_images_path);
    n_images = length(image_data_array);

    results = cell(n_images, 1);
    for i=1:n_images
        image_data = image_data_array{i}.pixels;
        bbox = image_data_array{i}.bbox;
        results{i} = menpobench.fit(image_data, bbox, model);
    end

    save(fullfile(testing_images_path, 'menpobench_test_results.mat'), 'results');

    exit(0);
end
