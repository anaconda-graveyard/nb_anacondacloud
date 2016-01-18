var t = casper.test;
function basic_test(){
  "use strict";
  this.baseline_notebook();

  this.thenEvaluate(function(username, password){
    require(['base/js/namespace'], function (Jupyter) {
      // clear out the auth token

    });
  });

  this.canSeeAndClick("the nbac button", "#publish_notebook");
}

casper.notebook_test(function(){
  casper.screenshot.init("00_basics");
  casper.viewport(1440, 900)
    .then(basic_test)
});
