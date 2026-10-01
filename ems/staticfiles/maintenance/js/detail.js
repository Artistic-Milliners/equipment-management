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
