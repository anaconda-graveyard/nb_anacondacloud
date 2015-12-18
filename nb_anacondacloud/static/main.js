define(['jquery'], function ($) {
    var showModal = function(title, body) {
        Jupyter.dialog.modal({
            title: title,
            body: body,
            buttons : {
                "OK": {}
            }
        });
    };

    var publishNotebook = function() {
        var anacondacloudid = IPython.notebook.metadata.anacondaCloudID,
            notebookName = IPython.notebook.notebook_name,
            nbj = IPython.notebook.toJSON(),
            interval;

        if (!IPython.notebook) return;
        $.ajax({
            url: "/ac-publish",
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            processData: false,
            data: JSON.stringify({
                name: notebookName,
                content: nbj
            })
        }).done(function(data) {
            IPython.notification_area.get_widget("notebook").
                set_message("Your notebook has been uploaded.", 4000);
            updateVisitLink(data.url);
        }).fail(function(jqXHR, textStatus) {
            var notif, title, body;
            if (jqXHR.status == 401) {
                notif = "Unauthorized";
                title = notif;
                body = $('<div>');
                $('<p>').text(
                    'You are not authorized to complete this actions. ' +
                    'From the command line run:'
                ).appendTo(body);
                $('<pre>').text('anaconda login').appendTo(body);
                showModal(title, body);
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
        if (!IPython.notebook) return;
        if (!anacondaCloudURL) {
            anacondaCloudURL = IPython.notebook.metadata.anacondaCloudURL;
        } else {
            IPython.notebook.metadata.anacondaCloudURL = anacondaCloudURL;
        }
        if (!anacondaCloudURL) {
            $('#visit_notebook').addClass('disabled');
        } else {
            $('#visit_notebook').removeClass('disabled').attr('data-url', anacondaCloudURL);
        }
        this.anacondaCloudURL = anacondaCloudURL;
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
                    'callback': publishNotebook,
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
