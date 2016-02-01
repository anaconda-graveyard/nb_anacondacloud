var t = casper.test;

var system = require('system');

function basic_test(){

  this.baseline_notebook();

  this.canSeeAndClick("the nbac toolbar button", "#publish_notebook")
    .then(function(){ return this.wait(300); })
    .canSeeAndClick("the upload header", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText("h4.modal-title", "Publish");
    })
    .canSeeAndClick("the publish button", ".modal-body .btn-success")
    .canSeeAndClick("the visit toolbar button", "#visit_notebook")
    .then(function(){ return this.wait(3000); })
    .canSeeAndClick("fin", "#publish_notebook");
}


casper.notebook_test(function(){
  casper.screenshot.init("auth_create");
  casper.viewport(1440, 900)
    .then(basic_test)
});
