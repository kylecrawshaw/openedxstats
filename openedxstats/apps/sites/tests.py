from django.test import TestCase
from management.commands.import_sites import import_data, check_for_required_cols
from django.core.management.base import CommandError
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.utils.six import StringIO
from django.http import HttpRequest
from .models import Site, GeoZone, Language
from .forms import SiteForm, GeoZoneForm, LanguageForm
from .views import add_site


class ImportScriptTestCase(TestCase):
    """
    Tests for import_sites management command.
    """

    def test_import_date_from_correctly_formatted_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 268\n"
                           "Number of languages imported: 34\n"
                           "Number of geozones imported: 58\n"
                           "Number of site_languages created: 271\n"
                           "Number of site_geozones created: 198\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source, stdout = out)
            self.assertIn(expected_output, out.getvalue())


    def test_import_wrongly_formatted_data_from_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/wrongly_formatted_data.csv"
        with open(source, 'rwb') as csvfile:
            with self.assertRaises(FieldDoesNotExist):
                import_data(csvfile)  # Import data

    def test_import_data_from_minimum_req_cols_csv(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/urls_only.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 3\n"
                           "Number of languages imported: 0\n"
                           "Number of geozones imported: 0\n"
                           "Number of site_languages created: 0\n"
                           "Number of site_geozones created: 0\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source, stdout=out)
            self.assertIn(expected_output, out.getvalue())

    def test_import_from_blank_csv_file(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/blank.csv"
        with open(source, 'rwb'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_import_from_wrong_file_type(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/text_file.txt"
        with open(source, 'rwb'):
            with self.assertRaises(CommandError):
                call_command('import_sites', source)

    def test_check_for_idempotency(self):
        source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv.csv"
        additional_source = "/Users/zacharyrobbins/Documents/postgres_data/edx_sites_csv_one_addition.csv"
        expected_output = ("Report:\n"
                           "Number of sites imported: 1\n"
                           "Number of languages imported: 0\n"
                           "Number of geozones imported: 2\n"
                           "Number of site_languages created: 1\n"
                           "Number of site_geozones created: 2\n")
        out = StringIO()
        with open(source, 'rwb'):
            call_command('import_sites', source)

        with open(additional_source, 'rwb'):
            call_command('import_sites', additional_source, stdout=out)
            self.assertIn(expected_output, out.getvalue())


class SubmitSiteFormTestCase(TestCase):
    """
    Tests for the add site form.
    """

    def test_form_validation_for_blank_url(self):
        form = SiteForm(data={'url':''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'], ['This field is required']
        )

    def test_form_validation_for_existing_url(self):
        new_site = Site(url='https://lagunitas.stanford.edu')
        new_site.save()
        form = SiteForm(data={'url': 'https://lagunitas.stanford.edu'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['url'], ['Site with this Url already exists.']
        )




    def test_add_a_single_site_with_all_fields(self):
        site = Site()
        request = HttpRequest()
        request.method = 'POST'
        # request.POST = {'site_type':'General',
        #              'name':'Test',
        #              'url':'https://convolutedurl.biz',
        #              'course_count':'1337',
        #              'last_checked':'06/13/2016',
        #              'org_type':'Academic',
        #              'language':['English', 'Chinese'],
        #              'geography':['US', 'China'],
        #              'github_fork':'Estranged-Spork',
        #              'notes':'What a day it is to be alive.',
        #              'course_type':'Righteous',
        #              'registered_user_count':'3333',
        #              'active_learner_count':'1111'
        #              }

        request.POST['site_type'] = 'General'
        request.POST['name'] = 'Test'
        request.POST['url'] = 'https://convolutedurl.biz'
        #request.POST['course_count'] = '1337'
        #request.POST['last_checked'] = '06/13/2016'
        #request.POST['org_type'] = 'Academic'
        #request.POST['geography'] = ['English', 'Chinese']
        #request.POST['github_fork'] = ['US', 'China']
        #request.POST['notes'] = 'Estranged-Spork'
        #request.POST['course_type'] = 'What a day it is to be alive.'
        #request.POST['registered_user_count'] = '3333'
        #request.POST['active_learner_count'] = '1111'

        self.assertEqual(0, len(Site.objects.all()))

        response = add_site(request)


        #response = self.client.post('/sites/add_site/', form_data)
        #print(response.content)
        #self.assertEqual(200, response.status_code)
        self.assertEqual(1, Site.objects.count())
        saved_site = Site.objects.first()
        #self.assertEqual(saved_site['url'], form_data['url'])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/sites/all')