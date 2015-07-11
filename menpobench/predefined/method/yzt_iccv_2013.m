function model_data = menpobench_train(training_images_path)
    %MENPOBENCH_TRAIN Summary of this function goes here
    %   Detailed explanation goes here

    %% Setup the AAM parameters for the training method.
    last_slash_index = find(training_images_path == filesep, 1, 'last');
    folder_name = training_images_path(last_slash_index + 1:end);
    parent_directory = training_images_path(1:last_slash_index);

    % Parameters taken from main_AAM
    pts_file_paths = dir([training_images_path '/*.pts']);
    first_pts_path = fullfile(training_images_path, pts_file_paths(1).name);
    AAM.num_of_points = size(menpobench_read_pts(first_pts_path), 2);
    AAM.scales = [1 2];
    AAM.shape.max_n = 136;
    num_of_scales = length(AAM.scales);
    AAM.texture = cell(1, num_of_scales);
    for ii = 1:num_of_scales
        AAM.texture{ii}.max_m = min(550, length(pts_file_paths));
    end
    
    %% Call training method
    AAM = train_AAM(parent_directory, folder_name, 'jpg', AAM);
    
    %% Truncate the AAM
    % This pre-computes a lot of data that makes fitting more efficient
    % Parameters taken from main_AAM
    cAAM.shape{1}.n = 10;
    cAAM.shape{2}.n = 3;
    cAAM.shape{1}.num_of_similarity_eigs = 4;
    cAAM.shape{2}.num_of_similarity_eigs = 4;
    cAAM.shape{1}.n_all = cAAM.shape{1}.n + cAAM.shape{1}.num_of_similarity_eigs;
    cAAM.shape{2}.n_all = cAAM.shape{2}.n + cAAM.shape{2}.num_of_similarity_eigs;
    cAAM.texture{1}.m = 200;
    cAAM.texture{2}.m = 50;
    
    cAAM.num_of_points = AAM.num_of_points;
    cAAM.scales = AAM.scales;
    cAAM.coord_frame = AAM.coord_frame;
    
    for ii = 1:num_of_scales
        % shape
        cAAM.shape{ii}.s0 = AAM.shape.s0;
        cAAM.shape{ii}.S = AAM.shape.S(:, 1:cAAM.shape{ii}.n);
        cAAM.shape{ii}.Q = AAM.shape.Q;
        
        % texture
        cAAM.texture{ii}.A0 = AAM.texture{ii}.A0;
        cAAM.texture{ii}.A = AAM.texture{ii}.A(:, 1:cAAM.texture{ii}.m);
        cAAM.texture{ii}.AA0 = AAM.texture{ii}.AA0;
        cAAM.texture{ii}.AA = AAM.texture{ii}.AA(:, 1:cAAM.texture{ii}.m);
        
        % warp jacobian
        [cAAM.texture{ii}.dW_dp, cAAM.coord_frame{ii}.triangles_per_point] = create_warp_jacobian(cAAM.coord_frame{ii}, cAAM.shape{ii});
    end
    
    %% Return AAM as model data
    model_data = cAAM;
end
