"""Define the functions that handle various requests by returnig a view"""

import random
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Max, Subquery
from django.views import View
from django.http import HttpResponse
from django.contrib import messages

from sawaliram_auth.decorators import volunteer_permission_required
from dashboard.models import (
    QuestionArchive,
    Question,
    Answer,
    UncuratedSubmission,
    UnencodedSubmission,
    TranslatedQuestion,
    Dataset)

import pandas as pd


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class DashboardHome(View):

    def get(self, request):
        """Return the dashboard home view."""
        context = {
            'dashboard': 'True',
            'page_title': 'Dashboard Home'
        }
        return render(request, 'dashboard/home.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(volunteer_permission_required, name='dispatch')
class SubmitQuestionsView(View):

    def get(self, request):
        """Return the submit questions view."""
        context = {
            'dashboard': 'True',
            'page_title': 'Submit Questions'
        }
        return render(request, 'dashboard/submit-questions.html', context)

    def post(self, request):
        """Save dataset to archive and return success message"""

        # save the questions in the archive
        excel_sheet = pd.read_excel(request.FILES.get('excel_file'))
        columns = list(excel_sheet)

        column_name_mapping = {
            'Question': 'question_text',
            'Question Language': 'question_language',
            'English translation of the question': 'question_text_english',
            'How was the question originally asked?': 'question_format',
            'Context': 'context',
            'Date of asking the question': 'question_asked_on',
            'Student Name': 'student_name',
            'Gender': 'student_gender',
            'Student Class': 'student_class',
            'School Name': 'school',
            'Curriculum followed': 'curriculum_followed',
            'Medium of instruction': 'medium_language',
            'Area': 'area',
            'State': 'state',
            'Published (Yes/No)': 'published',
            'Publication Name': 'published_source',
            'Publication Date': 'published_date',
            'Notes': 'notes',
            'Contributor Name': 'contributor',
            'Contributor Role': 'contributor_role'
        }

        for index, row in excel_sheet.iterrows():
            question = QuestionArchive()

            # only save the question if the question field is non-empty
            if not row['Question'] != row['Question']:

                for column in columns:
                    column = column.strip()

                    # check if the value is not nan
                    if not row[column] != row[column]:

                        if column == 'Published (Yes/No)':
                            setattr(
                                question,
                                column_name_mapping[column],
                                True if row[column] == 'Yes' else False)
                        else:
                            setattr(
                                question,
                                column_name_mapping[column],
                                row[column].strip() if isinstance(row[column], str) else row[column])

                question.submitted_by = request.user
                question.save()

        # create an entry for the dataset
        dataset = Dataset()
        dataset.question_count = len(excel_sheet.index)
        dataset.submitted_by = request.user
        dataset.status = 'raw'
        dataset.save()

        # create raw file for archiving
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_filename = 'dataset_' + str(dataset.id) + '_raw.xlsx'
        writer = pd.ExcelWriter(
            os.path.join(BASE_DIR, 'assets/submissions/raw/' + raw_filename))
        excel_sheet.to_excel(writer, 'Sheet 1')
        writer.save()

        # create file for curation
        excel_sheet['Field of Interest'] = ''
        excel_sheet['dataset_id'] = dataset.id
        uncurated_filename = 'dataset_' + str(dataset.id) + '_uncurated.xlsx'
        writer = pd.ExcelWriter(
            os.path.join(BASE_DIR, 'assets/submissions/uncurated/' + uncurated_filename))
        excel_sheet.to_excel(writer, 'Sheet 1')
        writer.save()

        messages.success(request, 'Thank you for the questions! We will get to work preparing the questions to be answered and translated.')
        context = {
            'dashboard': 'True',
            'page_title': 'Submit Questions'
        }
        return render(request, 'dashboard/submit-questions.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ValidateExcelSheet(View):

    def post(self, request):
        """Validate excel sheet and return status/errors"""
        excel_sheet = pd.read_excel(request.FILES.get('excel_file'))

        file_errors = {}

        for index, row in excel_sheet.iterrows():
            row_errors = []

            if row['Question'] != row['Question']:
                row_errors.append('Question field cannot be empty')
            if row['Question Language'] != row['Question Language']:
                row_errors.append('Question Language field cannot be empty')
            if row['Context'] != row['Context']:
                row_errors.append('Context field cannot be empty')
            if row['Published (Yes/No)'] == 'Yes' and row['Publication Name'] != row['Publication Name']:
                row_errors.append('If the question was published, you must mention the publication name')
            if row['Contributor Name'] != row['Contributor Name']:
                row_errors.append('You must mention the name of the contributor')

            if row_errors:
                # Adding 2 to compensate for 0 indexing and header row in excel template
                file_errors['Row #' + str(index + 2)] = row_errors

        if file_errors:
            response = render(request, 'dashboard/includes/excel-validation-errors.html', {'errors': file_errors})
        else:
            response = 'validated'

        return HttpResponse(response)


@login_required
def get_view_questions_view(request):
    """Return the 'View Questions' view after applying filters, if any."""
    questions_superset = Question.objects.all().order_by('-created_on')

    states_list = questions_superset.order_by() \
                                    .values_list('state') \
                                    .distinct('state') \
                                    .values('state')

    questions = questions_superset
    states_to_filter_by = request.GET.getlist('states')

    if states_to_filter_by:
        questions = questions.filter(state__in=states_to_filter_by)

    context = {
        'questions': questions,
        'states_list': states_list,
        'states_to_filter_by': states_to_filter_by}

    return render(request, 'dashboard/view-questions.html', context)


@login_required
def get_answer_questions_list_view(request):
    """Return the view with list of unanswered questions"""

    unanswered_questions = Question.objects.exclude(
        id__in=Subquery(Answer.objects.all().values('question_id')))

    context = {
        'unanswered_questions': unanswered_questions}

    return render(request, 'dashboard/answer-questions-list.html', context)


@login_required
def get_answer_question_view(request, question_id):
    """Return the view to answer a question"""

    question_to_answer = Question.objects.get(pk=question_id)

    context = {
        'question': question_to_answer
    }
    return render(request, 'dashboard/answer-question.html', context)


@login_required
def get_curate_data_view(request):
    """Return the curate data view"""

    uncurated_submissions = UncuratedSubmission.objects \
        .filter(curated=False) \
        .order_by('-created_on')

    context = {
        'uncurated_submissions': uncurated_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),}

    return render(request, 'dashboard/curate-data.html', context)


@login_required
def get_encode_data_view(request):
    """Return the encode data view"""

    unencoded_submissions = UnencodedSubmission.objects \
        .filter(encoded=False) \
        .order_by('-created_on')

    context = {
        'unencoded_submissions': unencoded_submissions,
        'excel_file_name': 'excel' + str(random.randint(1, 999)),}

    return render(request, 'dashboard/encode-data.html', context)


def submit_curated_dataset(request):
    """Save the curated questions."""
    excel_sheet = pd.read_excel(request.FILES[request.POST['excel-file-name']])
    columns = list(excel_sheet)

    column_name_mapping = {
        'Question': 'question_text',
        'Question Language': 'question_language',
        'English translation of the question': 'question_text_english',
        'How was the question originally asked?': 'question_format',
        'Context': 'context',
        'Date of asking the question': 'question_asked_on',
        'Student Name': 'student_name',
        'Gender': 'student_gender',
        'Student Class': 'student_class',
        'School Name': 'school',
        'Curriculum followed': 'curriculum_followed',
        'Medium of instruction': 'medium_language',
        'Area': 'area',
        'State': 'state',
        'Published (Yes/No)': 'published',
        'Publication Name': 'published_source',
        'Publication Date': 'published_date',
        'Notes': 'notes',
        'Contributor Name': 'contributor',
        'Contributor Role': 'contributor_role',
        'id': 'id',
        'submission_id': 'submission_id'}

    for index, row in excel_sheet.iterrows():
        curated_question = Question()

        for column in columns:
            column = column.strip()

            # check if the value is not nan
            if not row[column] != row[column]:

                if column == 'Published (Yes/No)':
                    setattr(
                        curated_question,
                        column_name_mapping[column],
                        True if row[column] == 'Yes' else False)
                else:
                    setattr(
                        curated_question,
                        column_name_mapping[column],
                        row[column].strip() if isinstance(row[column], str) else row[column])

        curated_question.curated_by = request.user
        curated_question.save()

        # save the english translation from the
        # curated dataset to TranslatedQuestion
        if not row['English translation of the question'] != row['English translation of the question']:
            english_translation = TranslatedQuestion(
                question_id=Question.objects.get(pk=row['id']),
                question_text=row['English translation of the question'],
                language='english'
            )
            english_translation.save()

    # set curated=True for related UncuratedSubmission entry
    submission_id = list(excel_sheet['submission_id'])[0]
    uncurated_submission_entry = UncuratedSubmission.objects \
                                                    .get(submission_id=submission_id)
    uncurated_submission_entry.curated = True
    uncurated_submission_entry.save()

    # drop columns not required for encoding
    del excel_sheet['Question Language']
    del excel_sheet['How was the question originally asked?']
    del excel_sheet['Context']
    del excel_sheet['Date of asking the question']
    del excel_sheet['Student Name']
    del excel_sheet['Gender']
    del excel_sheet['Student Class']
    del excel_sheet['Curriculum followed']
    del excel_sheet['Medium of instruction']
    del excel_sheet['Published (Yes/No)']
    del excel_sheet['Publication Name']
    del excel_sheet['Publication Date']
    del excel_sheet['Contributor Name']
    del excel_sheet['Contributor Role']

    # add columns for encoding
    excel_sheet['Subject of class/session'] = ''
    excel_sheet['Question topic "R"elated or "U"nrelated to the topic or "S"ponteneous'] = ''
    excel_sheet['Motivation for asking question'] = ''
    excel_sheet['Type of information requested'] = ''
    excel_sheet['Source'] = ''
    excel_sheet['Curiosity index'] = ''
    excel_sheet['Urban/Rural'] = ''
    excel_sheet['Type of school'] = ''
    excel_sheet['Comments for coding rationale'] = ''
    excel_sheet['submission_id'] = submission_id

    # create and save excel file for encoding
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    excel_filename = 'unencoded_dataset_' \
        + str(submission_id) + '.xlsx'

    writer = pd.ExcelWriter(os.path.join(
            BASE_DIR, 'assets/submissions/unencoded/' + excel_filename))
    excel_sheet.to_excel(writer, 'Sheet 1')
    writer.save()

    # create an UnencodedSubmission entry
    unencoded_submission = UnencodedSubmission()
    unencoded_submission.submission_id = submission_id
    unencoded_submission.number_of_questions = len(excel_sheet.index)
    unencoded_submission.excel_sheet_name = excel_filename
    unencoded_submission.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def submit_encoded_dataset(request):
    """Save the encoding information to Question."""
    excel_sheet = pd.read_excel(request.FILES[request.POST['excel-file-name']])

    for index, row in excel_sheet.iterrows():
        question = Question.objects.get(pk=row['id'])

        question.submission_id = row['submission_id']
        question.subject_of_session = row['Subject of class/session']
        question.question_topic_relation = row['Question topic "R"elated or "U"nrelated to the topic or "S"ponteneous']
        question.motivation = row['Motivation for asking question']
        question.type_of_information = row['Type of information requested']
        question.source = row['Source']
        question.curiosity_index = row['Curiosity index']
        question.urban_or_rural = row['Urban/Rural']
        question.type_of_school = row['Type of school']
        question.comments_on_coding_rationale = row['Comments for coding rationale']
        question.encoded_by = request.user

        question.save()

    # set the UnencodedSubmission entry as curated
    unencoded_submission_entry = UnencodedSubmission \
        .objects.get(submission_id=list(excel_sheet['submission_id'])[0])
    unencoded_submission_entry.encoded = True
    unencoded_submission_entry.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def submit_answer(request):
    """Save the submitted answer for review"""
    new_answer = Answer()
    new_answer.question_id = Question.objects.get(pk=request.POST['question_id'])
    new_answer.answer_text = request.POST['rich-text-content']
    new_answer.answered_by = request.user
    new_answer.save()

    return render(request, 'dashboard/excel-submitted-successfully.html')


def get_error_404_view(request, exception):
    """Return the custom 404 page."""

    response = render(request, 'dashboard/404.html')
    response.status_code = 404  # Not Found
    return response


def get_work_in_progress_view(request):
    """Return work-in-progress view."""

    response = render(request, 'dashboard/work-in-progress.html')
    response.status_code = 501  # Not Implemented
    return response
