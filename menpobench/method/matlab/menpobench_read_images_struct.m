function menpobench_images = menpobench_read_images_struct(base_path)

    images_struct_path = fullfile(base_path, 'menpobench_images.mat');
    load(images_struct_path);
end
