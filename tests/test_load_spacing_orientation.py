# Copyright 2020 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

import nibabel
import numpy as np
from nibabel.processing import resample_to_output
from parameterized import parameterized

from monai.transforms.composables import AddChanneld, LoadNiftid, Spacingd

FILES = tuple(
    os.path.join(os.path.dirname(__file__), 'testing_data', filename)
    for filename in ('anatomical.nii', 'reoriented_anat_moved.nii'))


class TestLoadSpacingOrientation(unittest.TestCase):

    @parameterized.expand(FILES)
    def test_load_spacingd(self, filename):
        data = {'image': filename}
        data_dict = LoadNiftid(keys='image')(data)
        data_dict = AddChanneld(keys='image')(data_dict)
        res_dict = Spacingd(keys='image', pixdim=(1, 2, 3), diagonal=True)(data_dict)
        np.testing.assert_allclose(data_dict['image.affine'], res_dict['image.original_affine'])
        anat = nibabel.Nifti1Image(data_dict['image'][0], data_dict['image.affine'])
        ref = resample_to_output(anat, (1, 2, 3))
        np.testing.assert_allclose(res_dict['image.affine'], ref.affine)
        np.testing.assert_allclose(res_dict['image'].shape[1:], ref.shape)
        np.testing.assert_allclose(ref.get_fdata(), res_dict['image'][0])

    @parameterized.expand(FILES)
    def test_load_spacingd_rotate(self, filename):
        data = {'image': filename}
        data_dict = LoadNiftid(keys='image')(data)
        data_dict = AddChanneld(keys='image')(data_dict)
        affine = data_dict['image.affine']
        data_dict['image.affine'] = \
            np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]) @ affine
        res_dict = Spacingd(keys='image', pixdim=(1, 2, 3), diagonal=True)(data_dict)
        np.testing.assert_allclose(data_dict['image.affine'], res_dict['image.original_affine'])
        anat = nibabel.Nifti1Image(data_dict['image'][0], data_dict['image.affine'])
        ref = resample_to_output(anat, (1, 2, 3))
        np.testing.assert_allclose(res_dict['image.affine'], ref.affine)
        np.testing.assert_allclose(res_dict['image'].shape[1:], ref.shape)
        np.testing.assert_allclose(ref.get_fdata(), res_dict['image'][0])

    def test_load_spacingd_non_diag(self):
        data = {'image': FILES[1]}
        data_dict = LoadNiftid(keys='image')(data)
        data_dict = AddChanneld(keys='image')(data_dict)
        affine = data_dict['image.affine']
        data_dict['image.affine'] = \
            np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]) @ affine
        res_dict = Spacingd(keys='image', pixdim=(1, 2, 3), diagonal=False)(data_dict)
        # res_image = nibabel.Nifti1Image(res_dict['image'][0], res_dict['image.affine'])
        # nibabel.save(res_image, 'test.nii.gz')
        np.testing.assert_allclose(data_dict['image.affine'], res_dict['image.original_affine'])
        np.testing.assert_allclose(
            res_dict['image.affine'],
            np.array([[0., 0., 3., -27.599409], [0., 2., 0., -47.977585], [-1., 0., 0., 35.297897], [0., 0., 0., 1.]]))

    def test_load_spacingd_rotate_non_diag(self):
        data = {'image': FILES[0]}
        data_dict = LoadNiftid(keys='image')(data)
        data_dict = AddChanneld(keys='image')(data_dict)
        res_dict = Spacingd(keys='image', pixdim=(1, 2, 3), diagonal=False, mode='nearest')(data_dict)
        np.testing.assert_allclose(data_dict['image.affine'], res_dict['image.original_affine'])
        # res_image = nibabel.Nifti1Image(res_dict['image'][0], res_dict['image.affine'])
        # nibabel.save(res_image, 'test.nii.gz')
        np.testing.assert_allclose(
            res_dict['image.affine'],
            np.array([[-1., 0., 0., 32.], [0., 2., 0., -40.], [0., 0., 3., -16.], [0., 0., 0., 1.]]))


if __name__ == '__main__':
    unittest.main()