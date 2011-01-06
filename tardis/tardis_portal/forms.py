#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2010, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

'''
forms module

@author: Gerson Galang
'''

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from django.conf import settings


class LoginForm(AuthenticationForm):
    authMethod = forms.CharField()
    next = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        authMethodChoices = ()

        for authMethods in settings.AUTH_PROVIDERS:
            authMethodChoices += ((authMethods[0], authMethods[1]),)

        self.fields['authMethod'] = forms.CharField(widget=forms.Select(choices=authMethodChoices),
            label='Authentication Method')


class ChangeUserPermissionsForm(ModelForm):
    class Meta:
        from django.forms.extras.widgets import SelectDateWidget
        from tardis.tardis_portal.models import ExperimentACL
        model = ExperimentACL
        exclude = ('entityId', 'pluginId', 'experiment', 'aclOwnershipType',)
        widgets = {
            'expiryDate': SelectDateWidget(),
            'effectiveDate': SelectDateWidget()
        }


class ChangeGroupPermissionsForm(forms.Form):

    from django.forms.extras.widgets import SelectDateWidget

    canRead = forms.BooleanField(label='canRead', required=False)
    canWrite = forms.BooleanField(label='canWrite', required=False)
    canDelete = forms.BooleanField(label='canDelete', required=False)

    effectiveDate = forms.DateTimeField(label='Effective Date',
            widget=SelectDateWidget(), required=False)
    expiryDate = forms.DateTimeField(label='Expiry Date',
            widget=SelectDateWidget(), required=False)



class DatafileSearchForm(forms.Form):

    filename = forms.CharField(required=False, max_length=100)


# microscopy
class MXDatafileSearchForm(DatafileSearchForm):

    __DIFFRACTOMETER_CHOICES = (
        ('-', '-'),
        ('Synchrotron', 'Synchrotron'),
        ('Rotating Anode', 'Rotating Anode'),
        ('Tube', 'Tube'))
    diffractometerType = \
        forms.CharField(widget=forms.Select(choices=__DIFFRACTOMETER_CHOICES),
        label='Diffractometer Type')
    xraySource = forms.CharField(
        required=False, label='X-ray Source', max_length=20)
    crystalName = forms.CharField(
        required=False, label='Crystal Name', max_length=20)
    resolutionLimit = forms.IntegerField(
        required=False, label='Max Resolution Limit')
    xrayWavelengthFrom = forms.IntegerField(
        required=False, label='X-ray Wavelength From',
        widget=forms.TextInput(attrs={'size': '4'}))
    xrayWavelengthTo = forms.IntegerField(
        required=False, label='X-ray Wavelength To',
        widget=forms.TextInput(attrs={'size': '4'}))


def createLinkedUserAuthenticationForm(authMethods):
    """Create a LinkedUserAuthenticationForm and use the contents of
    authMethods to the list of options in the dropdown menu for
    authenticationMethod.

    """
    _authenticationMethodChoices = ()
    for authMethodKey in authMethods.keys():
        _authenticationMethodChoices += (
            (authMethodKey, authMethods[authMethodKey]), )

    fields = {}
    fields['authenticationMethod'] = \
        forms.CharField(label='Authentication Method',
        widget=forms.Select(choices=_authenticationMethodChoices),
        required=True)
    fields['username'] = forms.CharField(label='Username',
        max_length=30, required=True)
    fields['password'] = forms.CharField(required=True,
        widget=forms.PasswordInput(), label='Password', max_length=12)

    return type('LinkedUserAuthenticationForm', (forms.BaseForm, ),
                    {'base_fields': fields})


# infrared
class IRDatafileSearchForm(DatafileSearchForm):
    pass


class EquipmentSearchForm(forms.Form):

    key = forms.CharField(label='Short Name',
        max_length=30, required=False)
    description = forms.CharField(label='Description',
        required=False)
    make = forms.CharField(label='Make', max_length=60, required=False)
    model = forms.CharField(label='Model', max_length=60, required=False)
    type = forms.CharField(label='Type', max_length=60, required=False)
    serial = forms.CharField(label='Serial No', max_length=60, required=False)


class ImportParamsForm(forms.Form):

    username = forms.CharField(max_length=400, required=True)
    password = forms.CharField(max_length=400, required=True)
    params = forms.FileField()


class RegisterExperimentForm(forms.Form):

    username = forms.CharField(max_length=400, required=True)
    password = forms.CharField(max_length=400, required=True)
    xmldata = forms.FileField()
    experiment_owner = forms.CharField(max_length=400, required=False)
    originid = forms.CharField(max_length=400, required=False)


def createSearchDatafileForm(searchQueryType):

    from errors import UnsupportedSearchQueryTypeError
    from tardis.tardis_portal.models import ParameterName
    from tardis.tardis_portal import constants

    parameterNames = None

    if searchQueryType in constants.SCHEMA_DICT:
        parameterNames = \
            ParameterName.objects.filter(
            schema__namespace__in=[constants.SCHEMA_DICT[searchQueryType]\
            ['datafile'], constants.SCHEMA_DICT[searchQueryType]['dataset']],
            is_searchable='True')

        fields = {}

        fields['filename'] = forms.CharField(label='Filename',
                max_length=100, required=False)
        fields['type'] = forms.CharField(widget=forms.HiddenInput,
                initial=searchQueryType)

        for parameterName in parameterNames:
            if parameterName.is_numeric:
                if parameterName.comparison_type \
                    == ParameterName.RANGE_COMPARISON:
                    fields[parameterName.name + 'From'] = \
                        forms.DecimalField(label=parameterName.full_name
                            + ' From', required=False)
                    fields[parameterName.name + 'To'] = \
                        forms.DecimalField(label=parameterName.full_name
                            + ' To', required=False)
                else:
                    # note that we'll also ignore the choices text box entry
                    # even if it's filled if the parameter is of numeric type
                    # TODO: decide if we are to raise an exception if
                    #       parameterName.choices is not empty
                    fields[parameterName.name] = \
                        forms.DecimalField(label=parameterName.full_name,
                            required=False)
            else:  # parameter is a string
                if parameterName.choices != '':
                    fields[parameterName.name] = \
                        forms.CharField(label=parameterName.full_name,
                        widget=forms.Select(choices=__getParameterChoices(
                        parameterName.choices)), required=False)
                else:
                    fields[parameterName.name] = \
                        forms.CharField(label=parameterName.full_name,
                        max_length=255, required=False)

        return type('SearchDatafileForm', (forms.BaseForm, ),
                    {'base_fields': fields})
    else:
        raise UnsupportedSearchQueryTypeError(
            "'%s' search query type is currently unsupported" %
            (searchQueryType, ))


def createSearchExperimentForm():

    from django.forms.extras.widgets import SelectDateWidget
    from tardis.tardis_portal.models import ParameterName
    from tardis.tardis_portal import constants

    parameterNames = []

    for experimentSchema in constants.EXPERIMENT_SCHEMAS:
        parameterNames += \
            ParameterName.objects.filter(
            schema__namespace__iexact=experimentSchema,
            is_searchable='True')

    fields = {}

    fields['title'] = forms.CharField(label='Title',
            max_length=20, required=False)
    fields['description'] = forms.CharField(label='Experiment Description',
            max_length=20, required=False)
    fields['institutionName'] = forms.CharField(label='Institution Name',
            max_length=20, required=False)
    fields['creator'] = forms.CharField(label='Author\'s Name',
            max_length=20, required=False)
    fields['date'] = forms.DateTimeField(label='Experiment Date',
            widget=SelectDateWidget(), required=False)

    for parameterName in parameterNames:
        if parameterName.is_numeric:
            if parameterName.comparison_type \
                == ParameterName.RANGE_COMPARISON:
                fields[parameterName.name + 'From'] = \
                    forms.DecimalField(label=parameterName.full_name
                        + ' From', required=False)
                fields[parameterName.name + 'To'] = \
                    forms.DecimalField(label=parameterName.full_name
                        + ' To', required=False)
            else:
                # note that we'll also ignore the choices text box entry
                # even if it's filled if the parameter is of numeric type
                # TODO: decide if we are to raise an exception if
                #       parameterName.choices is not empty
                fields[parameterName.name] = \
                    forms.DecimalField(label=parameterName.full_name,
                        required=False)
        else:  # parameter is a string
            if parameterName.choices != '':
                fields[parameterName.name] = \
                    forms.CharField(label=parameterName.full_name,
                    widget=forms.Select(choices=__getParameterChoices(
                    parameterName.choices)), required=False)
            else:
                fields[parameterName.name] = \
                    forms.CharField(label=parameterName.full_name,
                    max_length=255, required=False)

    return type('SearchExperimentForm', (forms.BaseForm, ),
                    {'base_fields': fields})


def __getParameterChoices(choicesString):
    """Handle the choices string in this format:
    '(hello:hi how are you), (yes:i am here), (no:joe)'

    Note that this parser is very strict and is not smart enough to handle
    any extra unknown characters that the user might put in the choices
    textbox.

    """

    import string
    import re
    paramChoices = ()

    # we'll always add '-' as the default value for a dropdown menu just
    # incase the user doesn't specify a value they'd like to search for
    paramChoices += (('-', '-'),)
    dropDownEntryPattern = re.compile(r'\((.*):(.*)\)')

    dropDownEntryStrings = string.split(choicesString, ',')
    for dropDownEntry in dropDownEntryStrings:
        dropDownEntry = string.strip(dropDownEntry)
        (key, value) = dropDownEntryPattern.search(dropDownEntry).groups()
        paramChoices += ((str(key), str(value)),)

    return paramChoices


def createSearchDatafileSelectionForm():

    from tardis.tardis_portal import constants

    supportedDatafileSearches = (('-', 'Datafile'),)
    for key in constants.SCHEMA_DICT:
        supportedDatafileSearches += ((key, key.upper()),)

    fields = {}
    fields['type'] = \
        forms.CharField(label='type',
        widget=forms.Select(choices=supportedDatafileSearches),
        required=False)
    fields['type'].widget.attrs['class'] = 'searchdropdown'

    return type('DatafileSelectionForm', (forms.BaseForm, ),
                    {'base_fields': fields})


