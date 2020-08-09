import traceback

from django.shortcuts import render
from django.views.generic import TemplateView, View

from .forms import TestMailForm
from .mixins import SuperUserRequiredMixin


class IndexView(SuperUserRequiredMixin, TemplateView):
    template_name = "simple_sendgrid/index.html"


class TestView(SuperUserRequiredMixin, View):
    template_name = "simple_sendgrid/test.html"

    def get(self, request, *args, **kwargs):
        test_mail_form = TestMailForm()
        context = dict(form=test_mail_form)
        return render(self.request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        test_mail_form = TestMailForm(request.POST)
        message = None
        if test_mail_form.is_valid():
            try:
                test_mail_form.send_mail()
            except Exception as e:
                message = traceback.format_exc()
            else:
                message = "Success! The email should have been sent to {}".format(
                    test_mail_form.cleaned_data["to"]
                )
        else:
            message = "Invalid data"

        context = dict(form=test_mail_form, message=message)

        return render(self.request, self.template_name, context=context)
