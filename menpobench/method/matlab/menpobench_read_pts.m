function p_mat = menpobench_read_pts( pts_path )
    file_id = fopen(pts_path);
    n_points = textscan(file_id, '%s %f', 1, 'HeaderLines', 1);
    points = textscan(file_id, '%f %f' , n_points{2}, 'MultipleDelimsAsOne', 1, 'Headerlines', 2);
    p_mat = cell2mat(points)';
end