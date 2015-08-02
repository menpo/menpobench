function funcs = menpobench_namespace()
    % Use a struct in matlab to simulate a Python namespace
    funcs.train = @train;
    funcs.setup = @setup;
    funcs.fit = @fit;
end

%% Fill in the functions below. These functions are then wired up into a struct
%  above to simulate a Python namespace. There are three functions to specify:
%    1. model_data = train(training_images_path)
%       This function is used to train the method. It should drop out a single
%       variable of any type (model_data), which can be any valid Matlab
%       type. This will be loaded using the 'setup' function and then passed
%       into the 'fit' function for generating the results.
%    2. model_data = setup()
%       This function is used to load the model data or setup any other
%       requirements for the 'fit' method. It will be called before
%       'fit' is called over each image in the test set.
%    3. result = fit(image_data, bbox, model_data)
%       Fit the given image from the given bounding box. The model data is
%       also provided to the fit method.

%% Train
function model_data = train(training_images_path)
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
    cAAM.shape{1}.n = min(10, length(pts_file_paths));
    cAAM.shape{2}.n = min(3, length(pts_file_paths));
    cAAM.shape{1}.num_of_similarity_eigs = 4;
    cAAM.shape{2}.num_of_similarity_eigs = 4;
    cAAM.shape{1}.n_all = cAAM.shape{1}.n + cAAM.shape{1}.num_of_similarity_eigs;
    cAAM.shape{2}.n_all = cAAM.shape{2}.n + cAAM.shape{2}.num_of_similarity_eigs;
    cAAM.texture{1}.m = min(200, length(pts_file_paths));
    cAAM.texture{2}.m = min(50, length(pts_file_paths));
    
    cAAM.num_of_points = AAM.num_of_points;
    cAAM.scales = AAM.scales;
    cAAM.coord_frame = AAM.coord_frame;
    
    for ii = 1:num_of_scales
        % MENPOBENCH: This is a new line added to store the number of iterations per scale.
        cAAM.num_of_iter{ii} = 50;
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

%% Setup
function model = setup(method_path)
    load(fullfile(method_path, 'model.mat'));
end

%% Fit
function result = fit(image_data, bbox, model_data)
    % Convert the image to float greyscale
    image_data = double(rgb2gray(image_data)) / 255;
    cAAM = model_data;

    %% initialization
    s0 = cAAM.shape{1}.s0;
    current_shape = menpobench_initial_shape_to_bbox(bbox, s0);
    num_of_scales_used = length(cAAM.scales);

    %% Fitting an AAM using Fast-SIC algorithm
    sc = 2 .^ (cAAM.scales-1);
    for ii = num_of_scales_used:-1:1
        current_shape = current_shape / sc(ii);

        % indices for masking pixels out
        ind_in = cAAM.coord_frame{ii}.ind_in;
        ind_out = cAAM.coord_frame{ii}.ind_out;
        ind_in2 = cAAM.coord_frame{ii}.ind_in2;
        ind_out2 = cAAM.coord_frame{ii}.ind_out2;
        resolution = cAAM.coord_frame{ii}.resolution;

        A0 = cAAM.texture{ii}.A0;
        A = cAAM.texture{ii}.A;
        AA0 = cAAM.texture{ii}.AA0;
        AA = cAAM.texture{ii}.AA;

        for i = 1:cAAM.num_of_iter{ii}

            % Warp image
            Iw = warp_image(cAAM.coord_frame{ii}, current_shape*sc(ii), image_data);
            I = Iw(:); I(ind_out) = [];
            II = Iw(:); II(ind_out2) = [];

            % compute reconstruction Irec
            if (i == 1)
                c = A'*(I - A0) ;
            else
                c = c + dc;
            end
            Irec = zeros(resolution(1), resolution(2));
            Irec(ind_in) = A0 + A*c;

            % compute gradients of Irec
            [Irecx Irecy] = gradient(Irec);
            Irecx(ind_out2) = 0; Irecy(ind_out2) = 0;
            Irec(ind_out2) = [];
            Irec = Irec(:);

            % compute J from the gradients of Irec
            J = image_jacobian(Irecx, Irecy, cAAM.texture{ii}.dW_dp, cAAM.shape{ii}.n_all);
            J(ind_out2, :) = [];

            % compute Jfsic and Hfsic
            Jfsic = J - AA*(AA'*J);
            Hfsic = Jfsic' * Jfsic;
            inv_Hfsic = inv(Hfsic);

            % compute dp (and dq) and dc
            dqp = inv_Hfsic * Jfsic'*(II-AA0);
            dc = AA'*(II - Irec - J*dqp);

            % This function updates the shape in an inverse compositional fashion
            current_shape =  compute_warp_update(current_shape, dqp, cAAM.shape{ii}, cAAM.coord_frame{ii});
        end
        current_shape(:,1) = current_shape(:, 1) * sc(ii) ;
        current_shape(:,2) = current_shape(:, 2) * sc(ii) ;
    end

    result = current_shape;
end
