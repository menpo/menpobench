function initial_shape = menpobench_initial_shape_to_bbox(bbox, mean_shape)
    %% BBox is a 4x1 vector = [min_x, min_y, max_x, max_y]
    %  mean_shape is a Nx2 vector representing the mean shape to initialise with
    %  Output is initial_shape, which is the mean_shape resized to fit within
    %  the bounding box.

    ms_bounds = [min(mean_shape), max(mean_shape)];
    mean_shape_bbox = [ms_bounds(1), ms_bounds(2); ms_bounds(3), ms_bounds(2); 
                       ms_bounds(3), ms_bounds(4); ms_bounds(1), ms_bounds(4)];
    bbox = [bbox(1), bbox(2); bbox(3), bbox(2); 
            bbox(3), bbox(4); bbox(1), bbox(4)];

    [~, ~, transform] = procrustes(bbox, mean_shape_bbox);

    c = repmat(transform.c(1, :), [size(mean_shape, 1), 1]);
    T = transform.T;
    b = transform.b;

    initial_shape = b * mean_shape * T + c;
end
