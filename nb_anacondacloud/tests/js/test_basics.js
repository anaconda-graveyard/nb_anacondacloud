var t = casper.test;


function basic_test(){

  this.baseline_notebook();

  this.canSeeAndClick("the nb_anacondacloud button", "#publish_notebook");
  this.canSeeAndClick("the modal cancel button", ".modal-dialog .btn[data-dismiss=modal]")
}

casper.notebook_test(function(){
  casper.viewport(1440, 900)
    .then(basic_test);
});
