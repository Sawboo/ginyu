(function($) {
    $(document).ready(function($) {

        // var getData = function (callback) {
        //   setTimeout(function () {
        //     callback.call(this, 'Hello World');
        //   }, 100);
        // }

        // var editor = new EpicEditor({
        //   basePath: '/static/epiceditor',
        //   textarea: 'textarea'
        // });
        // editor.load();

        // getData(function (data) {
        //     editor.importFile(null, data); });

        var opts = {
          container: 'epiceditor',
          basePath: '/static/epiceditor',
          clientSideStorage: false,
          useNativeFullsreen: true,
          parser: marked,
          file: {
            name: 'epiceditor',
            defaultContent: '',
            autoSave: false
          },
          theme: {
            base:'/themes/base/epiceditor.css',
            preview:'/themes/preview/github.css',
            editor:'/themes/editor/epic-dark.css'
          },
          focusOnLoad: false,
          shortcut: {
            modifier: 18,
            fullscreen: 70,
            preview: 80
          }
        }
        var editor = new EpicEditor(opts).load();

    });
})(django.jQuery);
