from menpobench.method import (managed_method,
                               save_images_to_dir, save_landmarks_to_dir,
                               train_matlab_method, MatlabWrapper)


def train(img_generator):
    with managed_method('yzt_iccv_2013', cleanup=False) as method_path:
        train_path = method_path / 'menpobench_train_images'
        images = list(img_generator)

        save_images_to_dir(images, train_path)
        save_landmarks_to_dir(images, 'gt', train_path)

        train_matlab_method(method_path, 'yzt_iccv_2013.m', train_path)

        return MatlabWrapper(method_path)
