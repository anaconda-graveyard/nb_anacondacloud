var system = require('system');

var t = casper.test,
  kernel_prefix = 'python',
  kernel_suffix = '';


casper.notebook_test_kernel(kernel_prefix, kernel_suffix, function(){
  casper.screenshot.init("auth_create");
  casper.viewport(1440, 900)
    .then(basic_test)
});


function basic_test(){
  this.baseline_notebook();

  return this.canSeeAndClick("the nbac toolbar button", "#publish_notebook")
    .then(function(){ return this.wait(300); })
    .canSeeAndClick("the upload header", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText("h4.modal-title", "Publish");
    })
    .canSeeAndClick("the publish button", ".modal-body .btn-success")
    .canSeeAndClick("the visit toolbar button", "#visit_notebook")
    .then(function(){ return this.wait(3000); })
    .canSeeAndClick("fin", "#publish_notebook")
    .then(function(){ return this.wait(3000); });
}
