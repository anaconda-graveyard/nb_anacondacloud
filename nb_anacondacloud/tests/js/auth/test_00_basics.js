var t = casper.test,
  kernel_prefix = 'python',
  kernel_suffix = '';


casper.notebook_test_kernel(kernel_prefix, kernel_suffix, function(){
  casper.screenshot.init("auth_basics");
  casper.viewport(1440, 900)
    .then(basic_test)
});


function basic_test(){
  "use strict";
  this.baseline_notebook();
  this.canSeeAndClick("the nbac button", "#publish_notebook");
}
