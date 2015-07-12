function menpobench_matlab_fit(method_path, testing_images_path)

    menpobench_addpath_recurse(method_path);
    menpobench = menpobench_namespace();

    model = menpobench.setup(method_path);

    image_data = [];
    bbox = [];
    result = menpobench.fit(image_data, bbox, model);

    exit(0);
end