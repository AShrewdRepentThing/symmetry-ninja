import itertools, pygame


def load_animation_frames_key_tween(image_file_stem,
                                     keyframe_range,
                                     tween_range):

    image_indices = itertools.product(keyframe_range, tween_range)
    return load_animation_frames(image_file_stem, image_indices)


def load_animation_frames(image_file_stem, image_indices, reverse=True):
    l_list, r_list = [], []
    imagefiles = [image_file_stem % entry for entry in image_indices]

    for imagefile in imagefiles:
        r_image = pygame.image.load(imagefile)
        r_list.append(r_image)

        if reverse:
            l_image = pygame.transform.flip(r_image, True, False)
            l_list.append(l_image)

    if reverse:
        return {'L': l_list, 'R': r_list}

    else:
        return r_list
