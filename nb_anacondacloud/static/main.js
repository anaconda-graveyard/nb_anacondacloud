define(['jquery', 'base/js/dialog', 'base/js/namespace'],
function ($, dialog, Jupyter) {
    'use strict';

    var NS = 'anaconda-cloud',
      THUMBNAIL_MIN_DIM = 48,
      LOGO_URL = 'http://binstar-static-prod.s3.amazonaws.com' +
        '/latest/img/AnacondaCloud_logo_green.png';

    function api(route){
      // reusable API mapping, handles
      return Jupyter.notebook.base_url + NS + '/' + route;
    }


    function metadata(key, value){
        // wrapper for metadata, ensuring the top-level namespace
        var md = Jupyter.notebook.metadata;

        // ensure top-level namespace is initialized
        md[NS] = md[NS] || {};

        if (!arguments.length) {
          return md[NS];
        } else if(arguments.length === 1){
          return md[NS][key];
        } else{
          md[NS][key] = value;
        }
    }


    function publishNotebook(){
        metadata('environment', metadata('attach-environment') ?
            Jupyter.notebook.kernel.name :
            null);
        Jupyter.notebook.save_notebook().then(uploadNotebook);
    }


    function uploadNotebook() {
        var interval;

        $.ajax({
              url: api('publish'),
              method: 'POST',
              dataType: 'json',
              contentType: 'application/json; charset=utf-8',
              processData: false,
              data: JSON.stringify({
                  name: Jupyter.notebook.notebook_name,
                  content: Jupyter.notebook.toJSON()
              })
          })
          .done(function(data) {
              Jupyter.notification_area.get_widget('notebook')
                  .set_message(Jupyter.notebook.notebook_name +
                      ' was published',
                      4000);
              metadata('url', data.url);
              Jupyter.notebook.save_notebook();
              updateVisitLink();
          })
          .fail(showError)
          .always(function(data, textStatus) {
              clearInterval(interval);
          });
        interval = uploadingNotification();
    }


    function visitNotebook() {
        var url = metadata('url');
        if (url) {
            var _window = window.open(url, '_blank');
            if (_window) {
                _window.focus();
            }
        }
    }


    function uploadingNotification() {
        var index = 0,
            pattern = ['-', '\\', '|', '/'],
            _updateString = function(i) {
                Jupyter.notification_area.
                    get_widget('notebook').
                    warning('Uploading ' + pattern[i]);
            }
        _updateString(index);
        return setInterval(function() {
            index+=1;
            if (index > 3) { index = 0 };
            _updateString(index);
        }, 250);
    }

    function updateVisitLink(){
        if (!metadata('url')) {
            $('#visit_notebook').addClass('hide');
        } else {
            $('#visit_notebook').removeClass('hide');
        }
    }


    function thumbnailable(){
        // find good candidate thumbnails
        return $('#notebook')
          .find('img, canvas')
          .filter(function(){
            return this.clientWidth > THUMBNAIL_MIN_DIM &&
              this.clientHeight > THUMBNAIL_MIN_DIM;
          });
    }


    function configureUpload(){
        var url,
            body,
            form,
            name,
            modal,
            attach,
            select,
            summary,
            adminUrl,
            thumbnail,
            thumbnails;

        Jupyter.notification_area.get_widget('notebook')
            .set_message('Connecting to Anaconda Cloud', 2000);

        $.ajax({
            url: api('login'),
            method: 'GET',
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
        }).done(function(data) {
            body = $('<div/>');
            name = Jupyter.notebook.notebook_name.replace(/.ipynb$/, '');

            // avoid any surprises with user events firing in the background
            Jupyter.notebook.keyboard_manager.register_events(body);

            url = metadata('url') || '';
            adminUrl = !url ? '' :
              url.replace('https://notebooks.', 'https://') + '/settings/admin';

            // actually build the form
            form = $('<div/>', {
                'class': 'form-horizontal',
                'role': 'form'
            }).appendTo(body);

            // provide prior publishing information
            if(url){
              $('<blockquote/>').append(
                  $('<span/>')
                      .text('This notebook was previously published as '),
                  $('<a/>', {href: url, target: '_blank'}).text(url)
              )
              .css({'border-left': 'solid 4px #43B02A'})
              .appendTo(body);
            }

            // warning about published status
            $('<p/>')
                .text('Initially, all published notebooks will be ').append(
                  $('<label/>', {'class': 'label label-default'})
                    .text('public'),
                  $('<span/>').text('. ')
                )
            .appendTo(body);

            // call to action to change settings
            if(adminUrl){
                $('<blockquote/>').append(
                    $('<span/>').text('Make '),
                    $('<strong/>').text(name),
                    $('<span/>').text(' '),
                    $('<label/>', {'class': 'label label-primary'})
                        .text('private'),
                    $('<span/>').text(' or '),
                    $('<label/>', {'class': 'label label-success'})
                        .text('authenticated'),
                    $('<span/>').text(' on the '),
                    $('<a/>', {href: adminUrl, target: '_blank'})
                        .text('Anaconda Cloud settings page'),
                    $('<span/>').text('.'))
                .appendTo(body);
            }

            // organization picker, if needed
            if (data.organizations && data.organizations.length) {
                select = $('<select/>', {
                        id: 'select-organization',
                        'class': 'form-control'
                    })

                $('<div/>', {'class': 'form-group'}).append(
                    $('<label/>', {'class': 'control-label col-sm-3'})
                        .text('User/Organization'),
                    $('<div/>', {'class': 'col-sm-9'}).append(select))
                .appendTo(form);

                [data.user].concat(data.organizations)
                    .forEach(function(org) {
                        $('<option/>', {value: org.login})
                            .text(org.login + ' (' + org.name + ')')
                            .appendTo(select);
                    });

                if (metadata('organization')) {
                    select.val(metadata('organization'));
                }
            }

            summary = $('<input/>', {
                'class': 'form-control',
                type: 'text',
                id: 'anaconda-summary',
                placeholder: 'A brief summary'
            })
            .val(metadata('summary'))
            .on('input', function(){
                metadata('summary', summary.val())
            });

            $('<div/>', {'class': 'form-group'}).append(
                $('<label/>', {'class': 'control-label col-sm-3'})
                    .text('Summary'),
                $('<div/>', {'class': 'col-sm-9'}).append(summary))
            .appendTo(form);

            // whether to include the environment in metadata
            attach = $('<input/>', {type: 'checkbox'}).prop({
                checked: metadata('attach-environment')})
                .on("change", function(){
                  metadata('attach-environment', attach.prop('checked'));
                });

            $('<div/>', {'class': 'form-group'}).append(
                $('<label/>', {'class': 'control-label col-sm-3'})
                    .text('Environment'),
                $('<div/>', {'class': 'col-sm-9'}).append(
                    $('<div/>', {'class': 'checkbox'}).append(
                        $('<label/>').append(attach,
                            $('<span/>').text('Attach conda environment')))))
            .appendTo(form);

            // thumbnails
            thumbnail = $('<img/>', {src: metadata('thumbnail'), height: 72});

            thumbnails = [];

            thumbnailable().map(function(){
                var canvas,
                  ctx,
                  uri;

                try{
                    switch(this.tagName.toLowerCase()){
                      case 'canvas':
                        canvas = this;
                        uri = canvas.toDataURL();
                        break;
                      case 'img':
                        canvas = $('<canvas/>').css({display: 'none'});
                        ctx = canvas[0].getContext('2d');
                        ctx.canvas.width = this.clientWidth;
                        ctx.canvas.height = this.clientHeight;
                        ctx.drawImage(this, 0, 0);
                        uri = canvas[0].toDataURL();
                        canvas.remove();
                        break;
                      default:
                        return;
                    }
                }catch (err){
                    console.log("couldn't snapshot", this, "perhaps execute the cell, perhaps?", err);
                    return;
                }

                thumbnails.push($('<li/>', {value: uri}).append(
                    $('<a/>')
                        .on('click', function(){
                            metadata('thumbnail', uri);
                            thumbnail.attr({src: uri})
                        })
                        .append($('<img/>', {src: uri, height: 100}))));
            });

            if(thumbnails.length){
              $('<div/>', {'class': 'form-group'}).append(
                  $('<label/>', {'class': 'control-label col-sm-3'})
                      .text('Thumbnail'),
                  $('<div/>', {'class': 'col-sm-9'}).append(
                      $('<div/>', {'class': 'dropdown'}).append(
                          $('<button/>', {
                              'class': 'btn btn-default dropdown-toggle',
                              'type': 'button',
                              'data-toggle': 'dropdown'
                          }).append(thumbnail),
                          $('<ul/>', {'class': 'dropdown-menu'})
                            .append(thumbnails)
                  )))
              .appendTo(form);
            }

            $('<div/>', {'class': 'form-group'}).append(
                $('<div/>', {'class': 'col-sm-9 col-sm-offset-3'}).append(
                    $('<button/>', {'class': 'btn btn-lg btn-success'})
                      .on('click', function(){
                        modal.modal('hide');
                        publishNotebook();
                      })
                      .append(
                        $('<i/>', {'class': 'fa fa-cloud-upload'}),
                        $('<span/>').text(' Publish')
                      )))
            .appendTo(form);

            // revert notebook CSS customizations to bootstrap default
            form.find('.control-label label')
                .css({'font-weight': 'bold'});
            form.find('.form-control')
                .css({margin: 0});
            form.find('.col-sm-3, .col-sm-9')
                .css({'padding-left': '15px', 'padding-right': '15px'});

            modal = dialog.modal({
                body: body,
                buttons: {
                    'Close': {}
                }
            });

            modal.find('.modal-title').append(
                $('<span/>').text('Publish '),
                $('<strong/>')
                  .text(name),
                $('<span/>').text(' to '),
                $('<a/>', {href: 'https://anaconda.org', target: '_blank'})
                  .append($('<img/>', {src: LOGO_URL, height: 32}))
            );

        }).fail(showError);
    }


    function showError(jqXHR, textStatus, label) {
        var notif, title, body;

        console.log(arguments)

        switch(jqXHR.status){
          case 401:
            title = 'Unauthorized';
            notif = [
              $('<p>').text('You are not authorized to complete this action.' +
                  ' You may need to run this at the command line:'),
              $('<pre>').text('anaconda login')
            ];
            break;
          case 500:
            title = label;
            notif = [
              $('<p>').text('An error ocurred in the Notebook Server'),
              $('<p>').text('You may need to re-install nb_anacondacloud')
            ];
            break;
          default:
            title = 'Error: ' + label;
            notif = [
              $('<p>').text('An error ocurred in the Notebook Server'),
            ]
        }

        Jupyter.notification_area.get_widget('notebook').
            danger(title, 4000);

        body = $('<div>').append(notif);

        dialog.modal({
            title: title,
            body: body,
            buttons : {
                OK: {}
            }
        });
    }


    function updateToolbar() {
        if (!Jupyter.toolbar) {
            $([Jupyter.events])
              .on('app_initialized.NotebookApp', updateToolbar);
            return;
        }
        if ($('#publish_notebook').length === 0) {
            Jupyter.toolbar.add_buttons_group([{
                label: 'Publish your notebook into Anaconda.org',
                icon: 'fa-cloud-upload',
                callback: configureUpload,
                id: 'publish_notebook'
            }, {
                label: 'Visit your notebook',
                icon: 'fa-cloud',
                callback: visitNotebook,
                id: 'visit_notebook'
            }]);
        }
        updateVisitLink();
    }

    function load_ipython_extension() {
        updateToolbar();
    }


    // export new and old API entrypoints
    return {
      load_ipython_extension: load_ipython_extension
    };
});
