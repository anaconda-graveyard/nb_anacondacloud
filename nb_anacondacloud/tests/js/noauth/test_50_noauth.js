var t = casper.test;

function noauth_test(){

  this.baseline_notebook();

  this.canSeeAndClick("ua the nbac button", "#publish_notebook")
    .canSeeAndClick("the notification area", "#notification_notebook")
    .canSeeAndClick("the modal", ".modal")
    .canSeeAndClick("the unauthorized message", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText(" h4.modal-title", "Sign in to");
    })
    .canSeeAndClick("the dismiss button",
      ".modal .btn[data-dismiss=modal]");
}

casper.notebook_test(function(){
  casper.screenshot.init("noauth");
  casper.viewport(1440, 900)
    .then(noauth_test)
});
