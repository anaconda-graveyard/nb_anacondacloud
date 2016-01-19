var t = casper.test;

var system = require('system');

function basic_test(){

  this.baseline_notebook();

  //this.runCell(0, ["!anaconda whoami"]);

  this.canSeeAndClick("the nbac button", "#publish_notebook")
    .then(function(){ return this.wait(300); })
    .canSeeAndClick("the upload header", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText("h4.modal-title", "Upload");
    })
    .canSeeAndClick("the ok button", ".modal-footer .btn-primary")
    .waitForText("Uploading")
    .canSeeAndClick("the uploading notification", "#notification_notebook")
    .waitForText("Your notebook has been uploaded")
    .canSeeAndClick("the success notification", "#notification_notebook")
    .then(function(){ return this.wait(3000); })
    .canSeeAndClick("fin", "#publish_notebook");
}


casper.notebook_test(function(){
  casper.screenshot.init("01_auth");
  casper.viewport(1440, 900)
    .then(basic_test)
});
