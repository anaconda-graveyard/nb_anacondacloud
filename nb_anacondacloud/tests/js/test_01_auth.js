var t = casper.test;

var system = require('system');

function basic_test(){

  this.baseline_notebook();

  this.canSeeAndClick("the nbac button", "#publish_notebook")
    .canSeeAndClick("the upload header", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText("h4.modal-title", "Upload");
    });
}


casper.notebook_test(function(){
  casper.screenshot.init("01_auth");
  casper.viewport(1440, 900)
    .then(basic_test)
});
