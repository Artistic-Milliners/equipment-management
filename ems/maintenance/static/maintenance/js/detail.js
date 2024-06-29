function createInputElem(value){
  ins
  var hiddenAction = document.createElement("input");
  var form = document.querySelector('#remarks-form')
  form.appendChild(hiddenAction)
  console.log("value")
  hiddenAction.type='hidden';
  hiddenAction.value=value;
  hiddenAction.name='status'
  hiddenAction.id='status'
  if (hiddenAction.value==='Rejected'){
    document.querySelector('#remarks-form').submit()
  }
  console.log('created hidden input')

}

