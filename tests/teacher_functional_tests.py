import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select


USERNAME = 'tedwhitrock'
PASSWORD = 'test'


class TeacherFunctionalTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.server_url = 'http://localhost:8000/student_growth_tracker/'
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def log_in(self):
        uname_input = self.browser.find_element_by_id('auth_user_username')
        uname_input.send_keys(USERNAME)
        pwd_input = self.browser.find_element_by_id('auth_user_password')
        pwd_input.send_keys(PASSWORD)
        pwd_input.send_keys(Keys.ENTER)

    def test_correct_page_loads(self):
        """
        Test that:

        #. the login page displays by default.
        """
        self.browser.get(self.server_url)

        # Get the "logo" text to make sure we're on the correct page.
        self.assertIn('Student Growth Tracker', self.browser.title)
        logo_text = self.browser.find_element_by_id('web2py-logo').text
        self.assertIn('Student Growth Tracker', logo_text)

    def test_teacher_can_log_in(self):
        """
        Test that:

        #. the teacher can log in,
        #. the gradebook is displayed upon login.
        """
        self.browser.get(self.server_url)

        self.log_in() # Gradebook

        header = self.browser.find_element_by_tag_name('h1').text
        self.assertIn("Ted Whitrock's Gradebook", header)

    def test_teacher_can_view_class(self):
        """
        Test that:

        #. the teacher can access the overview for a specific class.
        """
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One').click() # Math One class overview

        # The first 'h1' tag should have a link with text == class name.
        header = self.browser.find_element_by_xpath('//h1/a').text
        self.assertIn('Math One', header)

    def test_teacher_can_view_class_details(self):
        """
        Test that:

        #. the teacher can access the grade details for a specific class.
        """
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One').click() # Math One class overview
        self.browser.find_element_by_link_text('Math One').click() # Math One class details

        # The first 'h1' text should contain the class name.
        header = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Math One', header)

    def test_teacher_grade_table_displays(self):
        """
        Test that:

        #. the teacher can view the grade detail table for a specific class.
        """
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One').click() # Math One class overview
        self.browser.find_element_by_link_text('Math One').click() # Math One class details

        # Find the div that should contain the table of grades.
        grade_container = self.browser.find_element_by_id('student_grades')
        self.assertIsNotNone(grade_container)

        # Find the table that contains the grades.
        grade_table = grade_container.find_element_by_tag_name('table')
        self.assertIsNotNone(grade_table)

        header_row = grade_table.find_element_by_tag_name('tr')
        header_columns = header_row.find_elements_by_tag_name('td')
        self.assertEqual('Math Assignment Eleven', header_columns[1].text)

    def test_teacher_add_new_assignment(self):
        """
        Test that:

        #. the teacher can create a new assignment for the class.
        #. the assignment shows up in the grade table.
        """
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One').click() # Math One class overview
        self.browser.find_element_by_link_text('Math One').click() # Math One class details

        grade_container = self.browser.find_element_by_id('student_grades')
        grade_table = grade_container.find_element_by_tag_name('table')
        header_row = grade_table.find_element_by_tag_name('tr')
        header_columns = header_row.find_elements_by_tag_name('td')
        num_assignments = len(header_columns)

        # Check that the "Create new assignment" button takes us to
        # the create assignment page.
        new_assignment_button = self.browser.find_element_by_xpath("//div[@class='col-sm-12']/button")
        new_assignment_button.click()

        # Make sure we've landed on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Add a name
        assignment_name_input = self.browser.find_element_by_id('no_table_name')
        assignment_name_input.send_keys('new test assignment')

        # Add a grade type
        grade_type_selector = Select(self.browser.find_element_by_id('no_table_grade_type'))
        grade_type_selector.select_by_visible_text('Assignment')

        # Add a score
        score_input = self.browser.find_element_by_id('no_table_score')
        score_input.send_keys('20')

        # Add a standard
        standard_selector = Select(self.browser.find_element_by_id('no_table_standard'))
        standard_selector.select_by_value('10')

        # Submit the new grade.
        submit_button = self.browser.find_element_by_xpath("//input[@type='submit']")
        submit_button.click()

        # Make sure we've redirected back to the grade deatils page.
        header = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Math One', header)

        # Find the div that should contain the table of grades.
        updated_grade_container = self.browser.find_element_by_id('student_grades')
        self.assertIsNotNone(grade_container)

        # Find the table that contains the grades.
        updated_grade_table = updated_grade_container.find_element_by_tag_name('table')
        self.assertIsNotNone(grade_table)

        updated_header_row = updated_grade_table.find_element_by_tag_name('tr')
        updated_header_columns = updated_header_row.find_elements_by_tag_name('td')

        last_column_index = len(updated_header_columns) - 1
        new_assignment_column = updated_header_columns[last_column_index]

        self.assertEqual('new test assignment', new_assignment_column.text)
        self.assertEqual(num_assignments + 1, len(updated_header_columns))

    def test_teacher_add_new_assignment_requires_name(self):
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One')

        # Navigate directly to the new assignment page.
        self.browser.get(self.server_url + 'grades/create/2/2')

        # Make sure we're on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Add a grade type
        grade_type_selector = Select(self.browser.find_element_by_id('no_table_grade_type'))
        grade_type_selector.select_by_visible_text('Assignment')

        # Add a score
        score_input = self.browser.find_element_by_id('no_table_score')
        score_input.send_keys('20')

        # Add a standard
        standard_selector = Select(self.browser.find_element_by_id('no_table_standard'))
        standard_selector.select_by_value('10')

        # Submit without adding a grade type.
        submit_button = self.browser.find_element_by_xpath("//input[@type='submit']")
        submit_button.click()

        # Make sure we're still on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Find the error for the grade type.
        name_error = self.browser.find_element_by_id('name__error')
        self.assertIsNotNone(name_error)
        self.assertEqual('Enter a value', name_error.text)

    def test_teacher_add_new_assignment_requires_grade_type(self):
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One')

        # Navigate directly to the new assignment page.
        self.browser.get(self.server_url + 'grades/create/2/2')

        # Make sure we're on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Add a name
        assignment_name_input = self.browser.find_element_by_id('no_table_name')
        assignment_name_input.send_keys('new test assignment')

        # Add a score
        score_input = self.browser.find_element_by_id('no_table_score')
        score_input.send_keys('20')

        # Add a standard
        standard_selector = Select(self.browser.find_element_by_id('no_table_standard'))
        standard_selector.select_by_value('10')

        # Submit without adding a grade type.
        submit_button = self.browser.find_element_by_xpath("//input[@type='submit']")
        submit_button.click()

        # Make sure we're still on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Find the error for the grade type.
        grade_type_error = self.browser.find_element_by_id('grade_type__error')
        self.assertIsNotNone(grade_type_error)
        self.assertEqual('Value not in database', grade_type_error.text)

    def test_teacher_add_new_assignment_requires_score(self):
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One')

        # Navigate directly to the new assignment page.
        self.browser.get(self.server_url + 'grades/create/2/2')

        # Make sure we're on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Add a name
        assignment_name_input = self.browser.find_element_by_id('no_table_name')
        assignment_name_input.send_keys('new test assignment')

        # Add a grade type
        grade_type_selector = Select(self.browser.find_element_by_id('no_table_grade_type'))
        grade_type_selector.select_by_visible_text('Assignment')

        # Add a standard
        standard_selector = Select(self.browser.find_element_by_id('no_table_standard'))
        standard_selector.select_by_value('10')

        # Submit without adding a grade type.
        submit_button = self.browser.find_element_by_xpath("//input[@type='submit']")
        submit_button.click()

        # Make sure we're still on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Find the error for the grade type.
        score_error = self.browser.find_element_by_id('score__error')
        self.assertIsNotNone(score_error)
        self.assertEqual('Enter a number greater than or equal to 0', score_error.text)

    def test_teacher_add_new_assignment_requires_standard(self):
        self.browser.get(self.server_url)

        self.log_in() # Gradebook
        self.browser.find_element_by_link_text('Math One')

        # Navigate directly to the new assignment page.
        self.browser.get(self.server_url + 'grades/create/2/2')

        # Make sure we're on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Add a name
        assignment_name_input = self.browser.find_element_by_id('no_table_name')
        assignment_name_input.send_keys('new test assignment')

        # Add a grade type
        grade_type_selector = Select(self.browser.find_element_by_id('no_table_grade_type'))
        grade_type_selector.select_by_visible_text('Assignment')

        # Add a score
        score_input = self.browser.find_element_by_id('no_table_score')
        score_input.send_keys('20')

        # Submit without adding a grade type.
        submit_button = self.browser.find_element_by_xpath("//input[@type='submit']")
        submit_button.click()

        # Make sure we're still on the create grade page.
        add_grade_header = self.browser.find_element_by_tag_name('h1')
        self.assertEqual('Create a Grade:', add_grade_header.text)

        # Find the error for the grade type.
        standard_error = self.browser.find_element_by_id('standard__error')
        self.assertIsNotNone(standard_error)
        self.assertEqual('Value not in database', standard_error.text)
