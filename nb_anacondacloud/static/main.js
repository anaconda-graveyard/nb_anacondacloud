define(['jquery'], function ($) {
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
            updateUploadLink(data.url);
        }).fail(function(jqXHR, textStatus) {
            var msg = '';
            if (jqXHR.status == 401) {
                msg = 'You must login though anaconda client.';
            } else {
                msg = 'There has been a problem. Try again.';
            }
            IPython.notification_area.get_widget("notebook").
                danger(msg, 4000);
        }).always(function(data, textStatus) {
            clearInterval(interval);
        });
        interval = uploadingNotification();
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

    var updateUploadLink = function(anacondaCloudURL) {
        if (!IPython.notebook) return;
        if (!anacondaCloudURL) {
            anacondaCloudURL = IPython.notebook.metadata.anacondaCloudURL;
        } else {
            IPython.notebook.metadata.anacondaCloudURL = anacondaCloudURL;
        }
        if (!anacondaCloudURL) {
            return;
        }
        var toolbar = IPython.toolbar.element;
        var link = toolbar.find("a#nbviewer");
        if (!link.length) {
            link = $('<a id="nbviewer" target="_blank"/>');
            toolbar.append(
                $('<span id="nbviewer_span"/>').append(link)
            );
        }
        link.attr("href", + anacondaCloudURL);
        link.text(anacondaCloudURL);
        IPython.notebook.save_notebook();
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
                },
            ]);
        }
        updateUploadLink();
    };

    var load_ipython_extension = function () {
        publishButton();
    };

    return {
        load_ipython_extension : load_ipython_extension,
    };
});
