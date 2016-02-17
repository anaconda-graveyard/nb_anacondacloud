var t = casper.test;
function basic_test(){
  "use strict";
  this.baseline_notebook();
  this.canSeeAndClick("the nbac button", "#publish_notebook");
}

casper.notebook_test(function(){
  casper.screenshot.init("auth_basics");
  casper.viewport(1440, 900)
    .then(basic_test)
});
