<<<<<<< HEAD
<<<<<<< HEAD
function createInputElem(value){
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
=======
=======
>>>>>>> loginPage
function createInputElem(value) {
  console.log("I am here");
  console.log(value); // Corrected log statement

  var form = document.querySelector('#remarks-form');
  var remarks = document.querySelector('#man-remarks');

  // Check if remarks are filled
  if (remarks.value.trim() === "") {
      remarks.setCustomValidity("Please provide remarks."); // Set custom validity message
      remarks.reportValidity(); // Trigger the built-in validation UI
      return; // Stop form submission
  } else {
      remarks.setCustomValidity(""); // Clear any previous custom validity message
<<<<<<< HEAD
>>>>>>> 0c4d5ed (login.html modified for desktop added button to detail approval page)
=======
>>>>>>> loginPage
  }

  // Check if hidden input already exists to prevent duplicate IDs
  var hiddenAction = document.querySelector('#status');
  if (!hiddenAction) {
      hiddenAction = document.createElement("input");
      hiddenAction.type = 'hidden';
      hiddenAction.name = 'status';
      hiddenAction.id = 'status';
      form.appendChild(hiddenAction);
  }

  hiddenAction.value = value;

  // Submit the form for both actions
  form.submit();

  console.log('Created hidden input and submitted form');
}
