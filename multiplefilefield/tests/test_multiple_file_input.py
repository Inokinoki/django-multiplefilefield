from django.test import TestCase
from multiplefilefield.widgets import MultipleFileInput
from multiplefilefield.fields import MultipleFileModelField
from multiplefilefield_example.models import TestMultipleFile
from bs4 import BeautifulSoup as bs


class MultipleFileInputTestCase(TestCase):
    def test_retrieve_multiple_file(self):
        """
        Test normal file without quote
        """
        model_normal = TestMultipleFile(name="1", files="[something.txt, else.txt, something_else.txt]")
        self.assertEqual(model_normal.name, "1")
        self.assertEqual(len(model_normal.files), 3)
        self.assertIn("something.txt", model_normal.files)
        self.assertIn("else.txt", model_normal.files)
        self.assertIn("something_else.txt", model_normal.files)

    def test_retrieve_multiple_quote_file(self):
        """
        Test normal file with quotes
        """
        model_normal = TestMultipleFile(name="2", files="['something.txt', 'else.txt', 'something_else.txt']")
        self.assertEqual(model_normal.name, "2")
        self.assertEqual(len(model_normal.files), 3)
        self.assertIn("something.txt", model_normal.files)
        self.assertIn("else.txt", model_normal.files)
        self.assertIn("something_else.txt", model_normal.files)

    def test_retrieve_multiple_double_quote_file(self):
        """
        Test file with different types of quotes
        """
        model_normal = TestMultipleFile(name="3",
                                        files="['\'something.txt\'', '\'el\'se.txt', '\"something_else.txt\"']")
        self.assertEqual(model_normal.name, "3")
        self.assertEqual(len(model_normal.files), 3)
        self.assertIn("'something.txt'", model_normal.files)
        self.assertIn("'el'se.txt", model_normal.files)
        self.assertIn('"something_else.txt"', model_normal.files)

    def test_retrieve_multiple_unicode_file(self):
        """
        Test file with unicode prefix
        """
        model_normal = TestMultipleFile(name="4", files="[u'something.txt', u'else.txt', u'something_else.txt']")
        self.assertEqual(model_normal.name, "4")
        self.assertEqual(len(model_normal.files), 3)
        self.assertIn("something.txt", model_normal.files)
        self.assertIn("else.txt", model_normal.files)
        self.assertIn("something_else.txt", model_normal.files)

    def test_retrieve_multiple_comma_file(self):
        """
        Test file with commas in file name
        """
        model_normal = TestMultipleFile(name="4", files="[u'some,thi,ng.txt', u'else.txt', u'something,else.txt']")
        self.assertEqual(model_normal.name, "4")
        self.assertEqual(len(model_normal.files), 3)
        self.assertIn("some,thi,ng.txt", model_normal.files)
        self.assertIn("else.txt", model_normal.files)
        self.assertIn("something,else.txt", model_normal.files)

    def test_compatibility_file_field(self):
        """
        Test Compatibility with Native FileField, we save only one file
        """
        model_single_file = TestMultipleFile(name="single_file", files="something.txt")
        self.assertEqual(1, len(model_single_file.files))
        self.assertIn('something.txt', model_single_file.files)

    def test_admin_file_input_render(self):
        """
        Test File Input renderer with values
        """
        model_normal = TestMultipleFile(name="input", files="[u'something.txt', u'else.txt', u'something_else.txt']")
        _input = MultipleFileInput()

        html = _input.render("input_name", model_normal.files)
        labels = bs(html, "html.parser")

        input_label = labels.find("input")

        self.assertIsNotNone(input_label)

        self.assertIsNotNone(input_label["type"])
        self.assertEqual(input_label["type"].lower(), "file")

        self.assertIsNotNone(input_label["name"])
        self.assertEqual(input_label["name"].lower(), "input_name")

        self.assertIsNotNone(input_label["multiple"])
        self.assertEqual(input_label["multiple"], '')

        file_link_tags = labels.find_all("a")
        self.assertEqual(3, len(file_link_tags))

        file_links = [tag["href"] for tag in file_link_tags]
        self.assertEqual(3, len(file_links))

        file_names = [tag.get_text() for tag in file_link_tags]
        self.assertEqual(3, len(file_names))
        self.assertIn("something.txt", file_names)
        self.assertIn("else.txt", file_names)
        self.assertIn("something_else.txt", file_names)

    def test_admin_file_input_empty_render(self):
        """
        Test File Input renderer
        """
        model_empty = TestMultipleFile(name="input", files="")
        _input = MultipleFileInput()

        html = _input.render("input_name", model_empty.files)
        labels = bs(html, "html.parser")

        input_label = labels.find("input")

        self.assertIsNotNone(input_label)

        self.assertIsNotNone(input_label["type"])
        self.assertEqual(input_label["type"].lower(), "file")

        self.assertIsNotNone(input_label["name"])
        self.assertEqual(input_label["name"].lower(), "input_name")

        self.assertIsNotNone(input_label["multiple"])
        self.assertEqual(input_label["multiple"], '')

        file_link_tags = labels.find_all("a")
        self.assertEqual(0, len(file_link_tags))

    def test_file_input_empty_render(self):
        """
        Test File Input renderer
        """
        _input = MultipleFileInput()

        html = _input.render("input_name", None)
        labels = bs(html, "html.parser")

        input_label = labels.find("input")

        self.assertIsNotNone(input_label)

        self.assertIsNotNone(input_label["type"])
        self.assertEqual(input_label["type"].lower(), "file")

        self.assertIsNotNone(input_label["name"])
        self.assertEqual(input_label["name"].lower(), "input_name")

        self.assertIsNotNone(input_label["multiple"])
        self.assertEqual(input_label["multiple"], '')

        file_link_tags = labels.find_all("a")
        self.assertEqual(0, len(file_link_tags))

    def tearDown(self):
        pass

