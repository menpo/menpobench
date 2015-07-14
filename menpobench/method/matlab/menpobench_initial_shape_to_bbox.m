function initial_shape = menpobench_initial_shape_to_bbox(bbox, mean_shape)
    %% BBox is a 4x1 vector = [min_x, min_y, max_x, max_y]
    %  mean_shape is a Nx2 vector representing the mean shape to initialise with
    %  Output is initial_shape, which is the mean_shape resized to fit within
    %  the bounding box.

    mean_shape_bounds = reshape([min(mean_shape), max(mean_shape)], [2, 2])';
    bbox = reshape(bbox, [2, 2])';

    [~, ~, transform] = procrustes(bbox, mean_shape_bounds);

    c = repmat(transform.c(1, :), [size(mean_shape, 1), 1]);
    T = transform.T;
    b = transform.b;

    initial_shape = b * mean_shape * T + c;
end
