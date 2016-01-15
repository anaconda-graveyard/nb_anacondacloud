var t = casper.test;


function noauth_test(){

  this.baseline_notebook();

  this.canSeeAndClick("ua the nbac button", "#publish_notebook")
    .waitForSelectorTextChange("#notification_notebook", function(){
      console.error("selector text changed");
      return this;
    })
    .canSeeAndClick("the notification area - ua", "#notification_notebook")
    .canSeeAndClick("the modal - ua", ".modal")
    .canSeeAndClick("the unauthorized message - ua", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText(" h4.modal-title", "Unauthorized");
    })
    .canSeeAndClick("the dismiss button - ua",
      ".modal .btn[data-dismiss=modal]");
}

casper.notebook_test(function(){
  casper.viewport(1440, 900)
    .then(noauth_test)
});
