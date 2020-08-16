from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import FieldEntries, Fields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


class UserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("email", "Email"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
            ("ip", "IP Address"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class PublicUserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class UserBaseForm(BaseForm):
    name = StringField("User Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password")
    website = StringField("Website")
    affiliation = StringField("Affiliation")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    type = SelectField("Type", choices=[("user", "User"), ("admin", "Admin")])
    verified = BooleanField("Verified")
    hidden = BooleanField("Hidden")
    banned = BooleanField("Banned")
    submit = SubmitField("Submit")


def UserEditForm(*args, **kwargs):
    class _UserEditForm(UserBaseForm):
        pass

        @property
        def extra(self):
            fields = []
            new_fields = Fields.query.all()
            user_fields = {}

            for f in FieldEntries.query.filter_by(user_id=self.obj.id).all():
                user_fields[f.field_id] = f.value

            for field in new_fields:
                form_field = getattr(self, f"fields[{field.id}]")
                form_field.data = user_fields.get(field.id, "")
                entry = (field.name, form_field)
                fields.append(entry)
            return fields

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    new_fields = Fields.query.all()
    for field in new_fields:
        setattr(_UserEditForm, f"fields[{field.id}]", StringField(field.name))

    return _UserEditForm(*args, **kwargs)


def UserCreateForm(*args, **kwargs):
    class _UserCreateForm(UserBaseForm):
        notify = BooleanField("Email account credentials to user", default=True)

        @property
        def extra(self):
            fields = []
            new_fields = Fields.query.all()

            for field in new_fields:
                form_field = getattr(self, f"fields[{field.id}]")
                entry = (field.name, form_field)
                fields.append(entry)
            return fields

    new_fields = Fields.query.all()
    for field in new_fields:
        setattr(_UserCreateForm, f"fields[{field.id}]", StringField(field.name))

    return _UserCreateForm(*args, **kwargs)
