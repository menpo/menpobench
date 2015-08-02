def save_landmarks_to_dir(images, label, out_path, output_ext='.pts'):
    from menpo.visualize import print_progress
    import menpo.io as mio
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving landmarks to disk')):
        mio.export_landmark_file(im.landmarks[label],
                                 out_path / '{}{}'.format(k, output_ext))


def images_to_mat(images, out_path, attach_ground_truth=False):
    import numpy as np
    from scipy.io import savemat
    as_fortran = np.asfortranarray

    image_dicts = []
    for im in images:
        bbox = im.landmarks['bbox'].lms.bounds()
        i_dict = {'pixels': as_fortran(im.rolled_channels()),
                  'bbox': as_fortran(1 + np.array(bbox)[:, ::-1].ravel())}
        if attach_ground_truth:
            i_dict['gt'] = as_fortran(1 + im.landmarks['gt'].lms.points[:, ::-1])
        image_dicts.append(i_dict)

    if not out_path.exists():
        out_path.mkdir(parents=True)
    mat_out_path = out_path / 'menpobench_images.mat'
    print('Serializing image data to Matlab file: {}'.format(mat_out_path))
    savemat(str(mat_out_path), {'menpobench_images': image_dicts})


def save_images_to_dir(images, out_path, output_ext='.jpg'):
    from menpo.visualize import print_progress
    import menpo.io as mio
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving images to disk')):
        mio.export_image(im, out_path / '{}{}'.format(k, output_ext))
