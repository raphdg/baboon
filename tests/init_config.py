import os
import sys
import errno
import unittest


from mock import Mock
from config import config
from initialize import Initializor
from errors.baboon_exception import BaboonException


class TestInitConfig(unittest.TestCase):


    def test_success(self):
        """ Tests if the instanciation of the Initializor class works
        """
        os.path.join = Mock(return_value="/foopath/.baboon")
        os.path.exists = Mock(return_value=False)
        raised = False
        os.mkdir = Mock()

        try:
            initializor = Initializor()
        except:
            raised = True

        self.assertEquals(raised, False)

    def test_folder_enoent(self):
        """ Tests if the path does not exist
        """
        os.path.join = Mock(return_value="/foopath/.baboon")

        os.mkdir = Mock()
        os.mkdir.side_effect = OSError(errno.ENOENT,
                                       'No such file or directory',
                                       '/foopath/.baboon')

        with self.assertRaisesRegexp(BaboonException, 'No such file or directory'):
            initializor = Initializor()

    def test_folder_enoent(self):
        """ Tests if the path already exist
        """
        os.path.join = Mock(return_value="/foopath/.baboon")

        os.mkdir = Mock()
        os.mkdir.side_effect = OSError(errno.EEXIST,
                                       'File exists',
                                       '/foopath/.baboon')

        with self.assertRaisesRegexp(BaboonException, 'File exists'):
            initializor = Initializor()

    def test_mkdir_failed(self):
        """ Tests if there's another error raised by os.mkdir
        """
        os.path.join = Mock(return_value="/foopath/.baboon")

        os.mkdir = Mock()
        os.mkdir.side_effect = OSError(errno.EPERM,
                                       'Operation not permitted',
                                       '/foopath/.baboon')

        with self.assertRaises(OSError):
            initializor = Initializor()

if __name__ == '__main__':
    unittest.main()