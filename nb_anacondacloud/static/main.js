define(['jquery', 'base/js/dialog'], function ($, dialog) {
    var publishNotebook = function() {
        var organization = this.find('select').val();

        Jupyter.notebook.metadata.anacondaOrganization = organization;
        Jupyter.notebook.save_notebook()
            .then(function() {
                uploadNotebook();
            });
    };

    var uploadNotebook = function() {
        var notebookName = IPython.notebook.notebook_name,
            anacondaOrganization = Jupyter.notebook.metadata.anacondaOrganization,
            nbj = IPython.notebook.toJSON(),
            interval;

        $.ajax({
            url: "/ac-publish",
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            processData: false,
            data: JSON.stringify({
                name: notebookName,
                organization: anacondaOrganization,
                content: nbj
            })
        }).done(function(data) {
            Jupyter.notification_area.get_widget("notebook").
                set_message("Your notebook has been uploaded.", 4000);
            Jupyter.notebook.metadata.anacondaCloudURL = data.url;
            Jupyter.notebook.save_notebook();
            updateVisitLink(data.url);
        }).fail(function(jqXHR, textStatus) {
            var notif, title, body;
            if (jqXHR.status == 401) {
                showUnauthorized();
            } else {
                notif = 'Error: ' + jqXHR.statusText;
            }
            IPython.notification_area.get_widget("notebook").
                danger(notif, 4000);
        }).always(function(data, textStatus) {
            clearInterval(interval);
        });
        interval = uploadingNotification();
    };

    var visitNotebook = function() {
        var url = $(this).attr("data-url");
        if (typeof url !== 'undefined') {
            var _window = window.open(url, '_blank');
            if (_window != undefined) {
                _window.focus();
            }
        }
    };

    var uploadingNotification = function() {
        var index = 0,
            pattern = ['-', '\\', '|', '/'],
            _updateString = function(i) {
                IPython.notification_area.
                    get_widget('notebook').
                    warning('Uploading ' + pattern[i]);
            }
        _updateString(index);
        return setInterval(function() {
            index+=1;
            if (index > 3) { index = 0 };
            _updateString(index);
        }, 250);
    };

    var updateVisitLink = function(anacondaCloudURL) {
        if (!anacondaCloudURL) {
            anacondaCloudURL = IPython.notebook.metadata.anacondaCloudURL;
        }
        if (!anacondaCloudURL) {
            $('#visit_notebook').addClass('disabled');
        } else {
            $('#visit_notebook').removeClass('disabled').attr('data-url', anacondaCloudURL);
        }
    };

    var configureUpload = function() {
        var body,
            label,
            select,
            title,
            dropdown;
        IPython.notification_area.get_widget("notebook").set_message("Loading", 2000);
        $.ajax({
            url: "/ac-login",
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
        }).done(function(data) {
            title = "Upload " + IPython.notebook.notebook_name;
            body = $('<div>');
            $('<p>').text(
                'You are going to save and upload ' + IPython.notebook.notebook_name + '.')
                .appendTo(body);
            if (typeof data.organizations !== 'undefined' && data.organizations.length > 0) {
                $('<label/>').text('Select your organization').appendTo(body);
                select = $('<select/>').attr('id', 'select-organization');
                $('<option/>').attr('value', data.user.login)
                    .text(data.user.name).appendTo(select);
                data.organizations.forEach(function(org, index) {
                    select.append($('<option/>').attr("value", org.login).text(org.name));
                });
                if (IPython.notebook.metadata.anacondaOrganization) {
                    select.val(IPython.notebook.metadata.anacondaOrganization);
                }
                select.appendTo(body);
            }
            body.append(
                "<p><strong>Note:</strong> your notebook will be public." +
                "You can make it private in the settings page in Anaconda.org."
            );
            dialog.modal({
                title: title,
                body: body,
                buttons : {
                    "OK": {class: 'btn-primary', click: publishNotebook},
                    "Cancel": {}
                }
            });
        }).fail(function(jqXHR, textStatus) {
            showUnauthorized();
        });
    };

    var showUnauthorized = function() {
        var title = "Unauthorized",
            body = $('<div>');
        IPython.notification_area.get_widget("notebook").danger(title, 2000);
        $('<p>').text(
            'You are not authorized to complete this action. ' +
            'From the command line run:'
        ).appendTo(body);
        $('<pre>').text('anaconda login').appendTo(body);
        dialog.modal({
            title: title,
            body: body,
            buttons : {
                "OK": {}
            }
        });
    };

    var publishButton = function() {
        if (!IPython.toolbar) {
            $([IPython.events]).on("app_initialized.NotebookApp", publishButton);
            return;
        }
        if ($("#publish_notebook").length === 0) {
            IPython.toolbar.add_buttons_group([
                {
                    'label'   : 'Publish your notebook into Anaconda.org',
                    'icon'    : 'fa-cloud-upload',
                    'callback': configureUpload,
                    'id'      : 'publish_notebook'
                }, {
                    'label'   : 'Visit your notebook',
                    'icon'    : 'fa-cloud',
                    'callback': visitNotebook,
                    'id'      : 'visit_notebook'
                }
            ]);
        }
        updateVisitLink();
    };

    var load_ipython_extension = function () {
        publishButton();
    };

    return {
        load_ipython_extension : load_ipython_extension,
    };
});
